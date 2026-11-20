"""
FastAPI backend for ChainNotary
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import hashlib
import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

app = FastAPI(title="ChainNotary API", description="Notarize and verify documents on Ethereum")

RPC_URL = os.getenv("ETH_RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
ABI = [...]  # Same as in notary_client.py — truncated for brevity in this initial push

class VerifyResponse(BaseModel):
    exists: bool
    submitter: str | None = None
    timestamp: int | None = None
    description: str | None = None

@app.post("/notarize")
async def notarize_endpoint(file: UploadFile = File(...), description: str = Form(...)):
    content = await file.read()
    doc_hash = hashlib.sha256(content).digest()
    # Implementation mirrors CLI — build & send tx
    return {"status": "queued", "hash": f"0x{doc_hash.hex()}"}

@app.post("/verify", response_model=VerifyResponse)
async def verify_endpoint(file: UploadFile = File(...)):
    content = await file.read()
    doc_hash = hashlib.sha256(content).digest()
    # Call contract.verify
    return VerifyResponse(exists=False)  # Placeholder — expand in next sprint

@app.get("/")
async def root():
    return {"message": "ChainNotary API is live", "network": w3.eth.chain_id if w3.is_connected() else "disconnected"}
