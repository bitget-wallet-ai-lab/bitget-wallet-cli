# Changelog

All notable changes to the Bitget Wallet CLI are documented here.

Format: date-based versioning (`YYYY.M.DD-N`), aligned with [bitget-wallet-skill](https://github.com/bitget-wallet-ai-lab/bitget-wallet-skill).

---

## [2026.3.3-1] - 2026-03-03

### Changed
- Version scheme aligned to date-based format (`YYYY.M.DD-N`), matching the skill repo
- Added `CHANGELOG.md`

### Added
- `bgw calldata` command — generate unsigned swap transaction data (was missing, skill had it)
- `--deadline` parameter for calldata command (transaction expiry in seconds, mitigates sandwich attacks)

### Audit
- ✅ `cli.py`: +45 lines — new `calldata` subcommand + argparse registration
- ✅ No dependency changes
- ✅ Aligns with skill repo feature parity

---

## [1.0.0] - 2026-02-20

### Added
- Initial release
- Commands: price, info, top, audit, kline, tx, batch-tx, history, swap, lp, send
- Human-friendly formatted output with `--json` raw mode
- Built-in public demo API credentials
- `pip install` support via pyproject.toml
