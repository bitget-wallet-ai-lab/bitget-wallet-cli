# Changelog

All notable changes to the Bitget Wallet CLI are documented here.

Format: date-based versioning (`YYYY.M.DD-N`), aligned with [bitget-wallet-skill](https://github.com/bitget-wallet-ai-lab/bitget-wallet-skill).

---

## [2026.3.31-1] - 2026-03-31

### Breaking Changes
- **API migration**: `bopenapi.bgwapi.io` (ToB API) → `copenapi.bgwapi.io` (Skill internal API)
- **Auth rewrite**: HMAC-SHA256 + API Key → SHA256 hash signing (BKHmacAuth), zero secrets
- **Removed**: `API_KEY`, `API_SECRET`, `PARTNER_CODE` env vars and all HMAC/base64 signing
- **Removed commands**: `swap`, `calldata`, `send`, `order-quote`, `order-create`, `order-submit`, `order-status`
- **Endpoint migration**: `/bgw-pro/market/` → `/market/`, `/bgw-pro/swapx/` → `/swap-go/swapx/`

### Added — Swap Flow (aligned with Skill)
- `bgw quote` — first quote with multi-market results, includes `requestId`
- `bgw confirm` — second quote with `mevProtection`, `features`, `gasLevel`
- `bgw make-order` — create order with `orderId`, returns unsigned txs
- `bgw send-order` — submit signed txs (JSON array)
- `bgw order-details` — query order status
- `bgw check-token` — pre-trade risk check
- `bgw token-list` — popular tokens per chain (with `isAllNetWork: 1`)

### Added — Token Analysis (12 commands)
- `bgw search` — v3 token search with ordering
- `bgw search-v2` — v2 broader search (DEX tokens)
- `bgw market` — price, MC, FDV, liquidity, holders, narratives
- `bgw dev` — developer history and rug rate analysis
- `bgw launchpad` — launchpad scanning with filters
- `bgw smart-kline` — K-line with smart money/KOL overlays
- `bgw dynamics` — trading dynamics across time windows
- `bgw txlist` — transaction list with tag filtering
- `bgw holders` — holder distribution and top holders
- `bgw profit` — profit address analysis
- `bgw top-profit` — top profitable addresses

### Added — Smart Money (1 command)
- `bgw smart-money` — KOL/smart money address ranking with filters

### Added — RWA Stock Trading (6 commands)
- `bgw rwa-list` — available RWA stocks
- `bgw rwa-config` — trading config
- `bgw rwa-info` — stock info (GET request)
- `bgw rwa-price` — pre-trade buy/sell price
- `bgw rwa-kline` — K-line for RWA stocks
- `bgw rwa-holdings` — user's RWA portfolio

### Added — Balance (1 command)
- `bgw balance` — batch balance + USD values with pretty display

### Added — Infrastructure
- `request_get` in `api.py` — GET request support with BKHmacAuth signing
- `BGW_WALLET_ID` env var for Social Login Wallet users
- `--tab-type` flag on quote for bridge/swap selection

### Security
- ✅ Zero hardcoded secrets (removed API Key/Secret/Partner Code)
- ✅ Single outbound target: `copenapi.bgwapi.io`
- ✅ No file system access, no dynamic code execution, no persistence
- ✅ SlowMist security review: 🟢 LOW risk

### Stats
- 36 CLI commands (was 14)
- 33 API endpoints covered (100% Skill parity)

---

## [2026.3.5-1] - 2026-03-05

### Added
- **Order Mode API**: 4 new commands for gasless + cross-chain swaps
  - `bgw order-quote` — get swap price with cross-chain and gasless support
  - `bgw order-create` — create order, receive unsigned tx/signature data
  - `bgw order-submit` — submit signed transactions
  - `bgw order-status` — query order lifecycle status (init → processing → success/failed)
- New chain: Morph (`morph`)

### Audit
- ✅ `cli.py`: 4 new commands + argparse entries, no existing logic changed
- ✅ All new endpoints use same `bopenapi.bgwapi.io` base URL
- ✅ Same auth mechanism (HMAC-SHA256 + Partner-Code)
- ✅ No new dependencies

---

## [2026.3.3-1] - 2026-03-03

### Changed
- Version scheme aligned to date-based format (`YYYY.M.DD-N`), matching the skill repo
- Added `CHANGELOG.md`

### Added
- `bgw calldata` command — generate unsigned swap transaction data (was missing, skill had it)
- `bgw batch-price` command — batch get token info for multiple tokens
- `--deadline` parameter for calldata command (transaction expiry in seconds, mitigates sandwich attacks)
- `--from-address`, `--from-symbol`, `--to-symbol` parameters for swap command
- `--from-symbol`, `--to-symbol` parameters for calldata command

### Fixed
- `bgw send` tx format aligned with skill: `id:chain:from:rawTx` (was `id:from:nonce:rawTx`)
- Chain code: `sui` → `suinet` to match API and skill documentation
- Added missing `matic` (Polygon) to supported chains

### Audit
- ✅ `cli.py`: new commands + parameter additions + send format fix
- ✅ No dependency changes
- ✅ Full parity with skill repo commands, parameters, and chain codes

---

## [1.0.0] - 2026-02-20

### Added
- Initial release
- Commands: price, info, top, audit, kline, tx, batch-tx, history, swap, lp, send
- Human-friendly formatted output with `--json` raw mode
- Built-in public demo API credentials
- `pip install` support via pyproject.toml
