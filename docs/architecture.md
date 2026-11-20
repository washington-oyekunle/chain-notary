# Architecture Overview

## On-Chain Component
`DocumentNotary.sol` uses a mapping from `bytes32` (SHA-256 hash) to a struct containing:
- submitter address
- block.timestamp
- optional description
- existence flag

This design ensures:
- Constant-time lookups
- No storage of sensitive data
- Gas-efficient (only hash + metadata)

## Off-Chain Python Layer
- `notary_client.py`: CLI for local file hashing + transaction submission via web3.py
- `app.py`: FastAPI for remote/API access (upload file → hash → notarize)

## Security Considerations
- Private keys never leave the client environment (use hardware wallets or env vars in production).
- Always verify the contract on Etherscan before trusting.
- Consider multi-sig for high-value notarizations in future versions.

## Extension Ideas
- Batch notarization with Merkle trees to reduce gas.
- Integration with IPFS for optional encrypted metadata.
- Support for EIP-712 typed data signatures.
