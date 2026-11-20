# ChainNotary 🔗

**A production-ready Python + Solidity toolkit for notarizing and verifying document hashes on Ethereum.**

Timestamp documents, contracts, IP, or any file forever on-chain. Only the SHA-256 hash is stored — full privacy, immutable proof of existence and ownership.

Perfect for legal teams, researchers, artists, and compliance workflows.

## Why ChainNotary?

- **Real-world usable**: CLI + REST API that works with any Ethereum network (mainnet, Sepolia, local Ganache/Anvil).
- **Privacy-first**: Never uploads document content, only cryptographic hash.
- **Owner-tracked**: Records submitter address, timestamp, and optional description.
- **Verification in one call**: Instantly check if a file was notarized and by whom.
- **Open-source, auditable, extensible**.

## Architecture

```
[File] → Python Client (SHA-256) → Web3.py → DocumentNotary.sol (on-chain mapping)
                ↓
         FastAPI REST API (optional)
```

## Quick Start

### 1. Prerequisites
- Python 3.10+
- An Ethereum node (Infura, Alchemy, or local)
- A wallet with some ETH for gas (testnet recommended)

### 2. Install
```bash
git clone https://github.com/washington-oyekunle/chain-notary.git
cd chain-notary
pip install -r requirements.txt
```

### 3. Configure
Create `.env`:
```
ETH_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY
PRIVATE_KEY=0xYourPrivateKey
CONTRACT_ADDRESS=0x...  # after deployment
```

### 4. Deploy Contract (Hardhat/Foundry recommended)
See `contracts/DocumentNotary.sol`. Deploy and set `CONTRACT_ADDRESS`.

### 5. Notarize a document
```bash
python python/notary_client.py notarize ./important-contract.pdf "Q4 2026 Partnership Agreement"
```

### 6. Verify
```bash
python python/notary_client.py verify ./important-contract.pdf
```

### 7. Run API
```bash
uvicorn python.app:app --reload
```

## Features Roadmap
- [x] Core Solidity contract with events
- [x] Python CLI client (web3.py)
- [x] FastAPI backend
- [ ] Merkle batching for gas savings
- [ ] Frontend (React + wagmi)
- [ ] Multi-chain support (Polygon, Base)
- [ ] IPFS integration for optional metadata

## Live Demo & Verification
(Contract to be deployed on Sepolia — update README with address and Etherscan link.)

## License
MIT

---
Built for an impressive, real-world GitHub portfolio. Contributions welcome.
