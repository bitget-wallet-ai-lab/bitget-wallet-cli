# Bitget Wallet CLI

On-chain data at your fingertips. Query token prices, market analysis, smart money tracking, RWA stocks, swap quotes, and more from your terminal.

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
bgw price sol                          # SOL native token
bgw price eth 0x6982...               # PEPE on Ethereum

# Detailed info + market data
bgw info eth 0x6982...
bgw market eth 0x6982...              # Price, MC, FDV, liquidity, narratives

# Search tokens
bgw search PEPE --chain eth
bgw search-v2 PEPE                    # Broader DEX search

# Rankings
bgw top topGainers -n 10
bgw top topLosers -n 10

# Security audit
bgw audit eth 0x6982...

# Developer rug check
bgw dev sol <contract>

# Launchpad scanning
bgw launchpad --chain sol --mc-min 10000

# K-line data
bgw kline eth 0x6982... -p 1h -n 24
bgw smart-kline eth 0x6982...         # With KOL/smart money overlays

# Trading analysis
bgw dynamics eth 0x6982...            # Buy/sell pressure
bgw txlist eth 0x6982... --size 20    # Recent transactions
bgw holders eth 0x6982...             # Top holders

# Profit analysis
bgw profit eth 0x6982...
bgw top-profit eth 0x6982...

# Smart money
bgw smart-money --period 7d -n 10
bgw smart-money --group 1 --chain sol  # Smart money on Solana

# RWA stocks
bgw rwa-list --chain bnb
bgw rwa-info NVDAon
bgw rwa-price NVDAon --chain bnb --side buy \
  --coin-contract 0x55d398... --address 0xYour
bgw rwa-kline NVDAon --period 1d
bgw rwa-holdings 0xYourAddress

# Swap quote
bgw quote --from-address 0xYour --from-chain eth --from-symbol ETH \
  --from-contract "" --from-amount 0.01 \
  --to-symbol USDT --to-contract 0xdAC17F...

# Cross-chain swap
bgw quote --from-address 0xYour --from-chain eth --from-symbol ETH \
  --from-contract "" --from-amount 0.1 \
  --to-chain bnb --to-symbol USDT --to-contract 0x55d398... \
  --tab-type bridge

# Token list & risk check
bgw token-list sol
bgw check-token eth 0x6982... --symbol PEPE

# Balance
bgw balance eth 0xd8dA6BF269...
bgw balance sol 75k14Ug2UC67...

# Transfer
bgw transfer-make --chain eth --contract 0xdAC17F958D2ee523a2206206994597C13D831ec7 \
  --from-address 0xYour --to-address 0xRecipient --amount 100
bgw transfer-make --chain base --contract 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  --from-address 0xYour --to-address 0xRecipient --amount 50 --gasless
bgw transfer-submit --order-id <orderId> --sig <signedTx>
bgw transfer-status --order-id <orderId>

# Raw JSON output (pipe-friendly)
bgw --json price sol
bgw --json top topGainers | jq '.[0]'
```

## Supported Chains

`eth` · `sol` · `bnb` · `base` · `arbitrum` · `trx` · `ton` · `suinet` · `optimism` · `matic` · `morph`

Use empty contract (or omit) for native tokens (ETH, SOL, BNB, etc.).

## Commands (39)

### Market Data
| Command | Description |
|---------|-------------|
| `bgw price` | Quick price lookup |
| `bgw info` | Detailed token info (price, market cap, holders, links) |
| `bgw market` | Market info + narratives + pool list |
| `bgw search` | v3 token search with ordering |
| `bgw search-v2` | v2 broader search (DEX tokens) |
| `bgw dev` | Developer history and rug rate |
| `bgw top` | Rankings (topGainers, topLosers, Hotpicks) |
| `bgw audit` | Security audit (honeypot, permissions, tax) |
| `bgw kline` | K-line / candlestick data |
| `bgw smart-kline` | K-line with smart money/KOL overlays |
| `bgw tx` | Transaction volume and trader stats |
| `bgw batch-tx` | Batch transaction stats |
| `bgw dynamics` | Trading dynamics across time windows |
| `bgw txlist` | Transaction list with tag filtering |
| `bgw holders` | Holder distribution and top holders |
| `bgw profit` | Profit address analysis |
| `bgw top-profit` | Top profitable addresses |
| `bgw lp` | Liquidity pool info |
| `bgw launchpad` | Launchpad scanning with filters |
| `bgw history` | Historical tokens by creation time |
| `bgw batch-price` | Batch price lookup |

### Smart Money
| Command | Description |
|---------|-------------|
| `bgw smart-money` | KOL/smart money address ranking with filters |

### RWA Stock Trading
| Command | Description |
|---------|-------------|
| `bgw rwa-list` | Available RWA stocks |
| `bgw rwa-config` | Trading config |
| `bgw rwa-info` | Stock info and market status |
| `bgw rwa-price` | Pre-trade buy/sell price |
| `bgw rwa-kline` | Stock K-line charts |
| `bgw rwa-holdings` | User's RWA portfolio |

### Swap
| Command | Description |
|---------|-------------|
| `bgw quote` | Multi-market swap quotes |
| `bgw confirm` | Confirm with chosen market |
| `bgw make-order` | Create order (unsigned txs) |
| `bgw send-order` | Submit signed transactions |
| `bgw order-details` | Track order status |
| `bgw check-token` | Pre-trade risk check |
| `bgw token-list` | Popular tokens per chain |

### Token Transfer
| Command | Description |
|---------|-------------|
| `bgw transfer-make` | Create transfer order (unsigned tx data, supports gasless) |
| `bgw transfer-submit` | Submit signed transfer transaction |
| `bgw transfer-status` | Poll transfer order status |

### Balance
| Command | Description |
|---------|-------------|
| `bgw balance` | Wallet token balances with USD values |

> ⚠️ **Amounts are human-readable** — use `--amount 100` for 100 USDT, NOT wei/lamports.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BGW_WALLET_ID` | _(empty)_ | Wallet ID for Social Login Wallet users (optional) |

No API key required — uses SHA256 hash signing (BKHmacAuth).

## Security

- Only communicates with `https://copenapi.bgwapi.io` — no other external endpoints
- No API keys or secrets — SHA256 hash signing with zero credentials
- No `eval()` / `exec()` or dynamic code execution
- No file system access outside the project directory
- No data collection, telemetry, or analytics
- No access to sensitive files (SSH keys, credentials, wallet files, etc.)
- Dependencies: `requests` only
- SlowMist security review: 🟢 LOW risk
- We recommend auditing the source yourself before installation

## Related Projects

- [bitget-wallet-skill](https://github.com/bitget-wallet-ai-lab/bitget-wallet-skill) — OpenClaw AI Agent skill
- [bitget-wallet-mcp](https://github.com/bitget-wallet-ai-lab/bitget-wallet-mcp) — MCP Server for Claude/Cursor/Windsurf

## License

MIT
