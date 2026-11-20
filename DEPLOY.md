# Deployment Guide

## Local Testing (Recommended First)
1. Install Foundry or Hardhat.
2. Deploy `contracts/DocumentNotary.sol` to Anvil/Ganache.
3. Set `ETH_RPC_URL=http://127.0.0.1:8545` and the deployed address.

## Testnet (Sepolia)
1. Get test ETH from a faucet.
2. Deploy via Remix, Hardhat, or Foundry.
3. Update `.env` with Infura/Alchemy RPC and private key of deployer.
4. Verify contract on Etherscan.

## Production Notes
- Use a dedicated hot wallet with limited funds for notarization fees.
- Monitor gas prices.
- Consider Layer 2 (Base, Polygon, Optimism) for lower costs in v2.

After deployment, update the README with the live contract address and a verification example.
