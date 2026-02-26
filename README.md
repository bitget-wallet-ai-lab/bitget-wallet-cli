# Bitget Wallet CLI

On-chain data at your fingertips. Query token prices, security audits, swap quotes, and more from your terminal.

## Prerequisites

- Python 3.11+
- pip (comes with Python)

## Install

```bash
pip install git+https://github.com/bitget-wallet-ai-lab/bitget-wallet-cli.git
```

Or clone and install locally:

```bash
git clone https://github.com/bitget-wallet-ai-lab/bitget-wallet-cli.git
cd bitget-wallet-cli
pip install -e .
```

Verify installation:

```bash
bgw --version
```

## Usage

```bash
# Token price
bgw price sol                          # SOL price
bgw price eth                          # ETH price
bgw price sol Es9vMF...               # SPL token by contract

# Detailed token info
bgw info sol
bgw info eth 0xdAC17F...              # USDT on Ethereum

# Top gainers / losers
bgw top gainers
bgw top losers -n 20

# Security audit
bgw audit sol <contract>

# K-line data
bgw kline sol <contract> -p 1h -n 24

# Transaction stats
bgw tx sol <contract>

# Swap quote (same-chain)
bgw swap --from-chain sol --to-contract EPjFWdd5... --amount 1

# Swap quote (cross-chain)
bgw swap --from-chain sol --to-chain eth --from-contract "" --to-contract 0xdAC17F... --amount 1

# Liquidity pools
bgw lp sol <contract>

# Raw JSON output (pipe-friendly)
bgw price sol --json
bgw top gainers --json | jq '.[0]'
```

## Supported Chains

`eth` · `sol` · `bnb` · `base` · `arbitrum` · `trx` · `ton` · `sui` · `optimism`

Use empty contract (or omit) for native tokens (ETH, SOL, BNB, etc.).

## Commands

| Command | Description |
|---------|-------------|
| `bgw price` | Quick price lookup |
| `bgw info` | Detailed token info (price, market cap, holders, links) |
| `bgw top` | Top gainers or losers rankings |
| `bgw audit` | Security audit (honeypot, permissions, blacklist) |
| `bgw kline` | K-line / candlestick data |
| `bgw tx` | Transaction volume and trader stats |
| `bgw swap` | Swap quote with best route (same-chain & cross-chain) |
| `bgw batch-tx` | Batch transaction stats for multiple tokens |
| `bgw history` | Discover new tokens by timestamp |
| `bgw lp` | Liquidity pool information |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BGW_API_KEY` | Built-in demo key | Bitget Wallet ToB API appId |
| `BGW_API_SECRET` | Built-in demo secret | Bitget Wallet ToB API apiSecret |
| `BGW_PARTNER_CODE` | `bgw_swap_public` | Partner code for swap endpoints |

> **Note:** The built-in demo keys are for testing purposes and may change over time. If they stop working, please update the CLI to get the latest keys.

## Related Projects

- [bitget-wallet-skill](https://github.com/bitget-wallet-ai-lab/bitget-wallet-skill) — OpenClaw AI Agent skill (with [platform compatibility guide](https://github.com/bitget-wallet-ai-lab/bitget-wallet-skill/blob/main/COMPATIBILITY.md))
- [bitget-wallet-mcp](https://github.com/bitget-wallet-ai-lab/bitget-wallet-mcp) — MCP Server for Claude/Cursor/Windsurf

## License

MIT
