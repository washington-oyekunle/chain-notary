#!/usr/bin/env python3
"""
ChainNotary CLI Client
Notarize and verify document hashes on Ethereum using web3.py
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

RPC_URL = os.getenv("ETH_RPC_URL", "http://127.0.0.1:8545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Minimal ABI for DocumentNotary
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
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

def sha256_file(path: Path) -> bytes:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.digest()

def get_web3():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("Failed to connect to Ethereum node")
        sys.exit(1)
    return w3

def get_contract(w3):
    if not CONTRACT_ADDRESS:
        print("CONTRACT_ADDRESS not set in .env")
        sys.exit(1)
    return w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

def notarize(file_path: str, description: str):
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    doc_hash = sha256_file(path)
    print(f"Document SHA-256: 0x{doc_hash.hex()}")

    w3 = get_web3()
    contract = get_contract(w3)
    account = w3.eth.account.from_key(PRIVATE_KEY)

    tx = contract.functions.notarize(doc_hash, description).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 200_000,
        "gasPrice": w3.eth.gas_price,
    })

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Notarized! Tx: {tx_hash.hex()}")
    print(f"Block: {receipt.blockNumber}")

def verify(file_path: str):
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    doc_hash = sha256_file(path)
    print(f"Checking SHA-256: 0x{doc_hash.hex()}")

    w3 = get_web3()
    contract = get_contract(w3)

    # Note: verify is nonpayable; in practice use .call() for view-like behavior
    result = contract.functions.verify(doc_hash).call()
    exists, submitter, timestamp, description = result

    if exists:
        print("✅ Document verified on-chain!")
        print(f"   Submitter: {submitter}")
        print(f"   Timestamp: {timestamp}")
        print(f"   Description: {description}")
    else:
        print("❌ Document not found on-chain.")

def main():
    parser = argparse.ArgumentParser(description="ChainNotary CLI")
    sub = parser.add_subparsers(dest="command")

    n = sub.add_parser("notarize", help="Notarize a file")
    n.add_argument("file")
    n.add_argument("description")

    v = sub.add_parser("verify", help="Verify a file")
    v.add_argument("file")

    args = parser.parse_args()

    if args.command == "notarize":
        notarize(args.file, args.description)
    elif args.command == "verify":
        verify(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
