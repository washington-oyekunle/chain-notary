"""
FastAPI backend for ChainNotary
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import hashlib
import os
from dotenv import load_dotenv
from web3 import Web3
from web3.exceptions import ContractLogicError

load_dotenv()

app = FastAPI(title="ChainNotary API", description="Notarize and verify documents on Ethereum")

RPC_URL = os.getenv("ETH_RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

ABI = [
    {
        "inputs": [{"name": "docHash", "type": "bytes32"}, {"name": "description", "type": "string"}],
        "name": "notarize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "docHash", "type": "bytes32"}],
        "name": "verify",
        "outputs": [
            {"name": "exists", "type": "bool"},
            {"name": "submitter", "type": "address"},
            {"name": "timestamp", "type": "uint256"},
            {"name": "description", "type": "string"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "submitter", "type": "address"}],
        "name": "getDocumentsBySubmitter",
        "outputs": [{"name": "", "type": "bytes32[]"}],
        "stateMutability": "view",
        "type": "function",
    },
]

def get_contract():
    if not CONTRACT_ADDRESS or not w3.is_connected():
        raise HTTPException(status_code=503, detail="Contract or RPC not configured")
    return w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

class VerifyResponse(BaseModel):
    exists: bool
    submitter: str | None = None
    timestamp: int | None = None
    description: str | None = None
    hash: str | None = None

class NotarizeResponse(BaseModel):
    status: str
    hash: str
    tx_hash: str | None = None
    message: str | None = None

@app.post("/notarize", response_model=NotarizeResponse)
async def notarize_endpoint(file: UploadFile = File(...), description: str = Form(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    doc_hash = hashlib.sha256(content).digest()
    hash_hex = f"0x{doc_hash.hex()}"

    if not PRIVATE_KEY:
        return NotarizeResponse(
            status="hash_only",
            hash=hash_hex,
            message="No PRIVATE_KEY set; use CLI or provide key to submit on-chain"
        )

    try:
        contract = get_contract()
        account = w3.eth.account.from_key(PRIVATE_KEY)
        tx = contract.functions.notarize(doc_hash, description).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 250_000,
            "gasPrice": w3.eth.gas_price,
        })
        signed = account.sign_transaction(tx)
        raw = getattr(signed, "rawTransaction", None) or getattr(signed, "raw_transaction", None)
        tx_hash = w3.eth.send_raw_transaction(raw)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return NotarizeResponse(
            status="success",
            hash=hash_hex,
            tx_hash=tx_hash.hex(),
            message=f"Mined in block {receipt.blockNumber}"
        )
    except ContractLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transaction failed: {e}")

@app.post("/verify", response_model=VerifyResponse)
async def verify_endpoint(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    doc_hash = hashlib.sha256(content).digest()
    hash_hex = f"0x{doc_hash.hex()}"

    try:
        contract = get_contract()
        exists, submitter, timestamp, description = contract.functions.verify(doc_hash).call()
        return VerifyResponse(
            exists=exists,
            submitter=submitter if exists else None,
            timestamp=timestamp if exists else None,
            description=description if exists else None,
            hash=hash_hex
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{address}")
async def list_documents(address: str):
    try:
        checksum = Web3.to_checksum_address(address)
        contract = get_contract()
        hashes = contract.functions.getDocumentsBySubmitter(checksum).call()
        return {"address": checksum, "count": len(hashes), "hashes": [f"0x{h.hex()}" for h in hashes]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    connected = w3.is_connected()
    return {
        "message": "ChainNotary API is live",
        "connected": connected,
        "network": w3.eth.chain_id if connected else None,
        "contract": CONTRACT_ADDRESS
    }
