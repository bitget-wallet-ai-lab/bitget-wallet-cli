"""Bitget Wallet CLI — on-chain data at your fingertips."""

import argparse
import json
import sys

from . import __version__
from .api import request
from .format import fmt_change, fmt_number, fmt_price, fmt_volume

CHAINS = {
    "eth": "1", "sol": "100278", "bnb": "56", "base": "8453",
    "arbitrum": "42161", "trx": "6", "ton": "100280",
    "sui": "100281", "optimism": "10",
}


def _get_token(chain: str, contract: str) -> dict | None:
    result = request("/bgw-pro/market/v3/coin/batchGetBaseInfo",
                     {"list": [{"chain": chain, "contract": contract}]})
    if "data" in result and "list" in result["data"] and result["data"]["list"]:
        return result["data"]["list"][0]
    return None


# ── Commands ──────────────────────────────────────────────────────────────

def cmd_price(args):
    """Get token price."""
    token = _get_token(args.chain, args.contract or "")
    if not token:
        print(f"Token not found on {args.chain}", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps({"symbol": token.get("symbol"), "price": token.get("price"),
                          "change_24h": token.get("change_24h")}, indent=2))
    else:
        print(f"{token.get('symbol', '?')}  {fmt_price(token.get('price'))}  {fmt_change(token.get('change_24h'))}")


def cmd_info(args):
    """Get detailed token info."""
    token = _get_token(args.chain, args.contract or "")
    if not token:
        print(f"Token not found on {args.chain}", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps(token, indent=2))
    else:
        print(f"{'Symbol:':<16} {token.get('symbol', '?')}")
        print(f"{'Name:':<16} {token.get('name', '?')}")
        print(f"{'Price:':<16} {fmt_price(token.get('price'))}")
        print(f"{'24h Change:':<16} {fmt_change(token.get('change_24h'))}")
        print(f"{'Market Cap:':<16} {fmt_volume(token.get('market_cap'))}")
        print(f"{'24h Volume:':<16} {fmt_volume(token.get('turnover_24h'))}")
        print(f"{'Holders:':<16} {fmt_number(token.get('holders'))}")
        print(f"{'Chain:':<16} {args.chain}")
        print(f"{'Contract:':<16} {args.contract or '(native)'}")
        socials = token.get("social_links") or token.get("socialLinks") or {}
        if socials:
            print(f"{'Links:':<16}", end="")
            parts = []
            for k, v in socials.items():
                if v:
                    parts.append(f"{k}: {v}")
            print(" | ".join(parts) if parts else "N/A")


def cmd_top(args):
    """Get top gainers or losers."""
    name = "topGainers" if args.type == "gainers" else "topLosers"
    result = request("/bgw-pro/market/v3/topRank/detail", {"name": name})
    items = result.get("data", {}).get("list", [])
    if args.json:
        print(json.dumps(items[:args.limit], indent=2))
    else:
        title = "🟢 Top Gainers" if args.type == "gainers" else "🔴 Top Losers"
        print(f"\n{title}")
        print(f"{'#':<4} {'Symbol':<12} {'Price':<16} {'24h Change':<14} {'Volume':<12}")
        print("-" * 60)
        for i, t in enumerate(items[:args.limit], 1):
            print(f"{i:<4} {t.get('symbol', '?'):<12} {fmt_price(t.get('price')):<16} "
                  f"{fmt_change(t.get('change_24h')):<14} {fmt_volume(t.get('turnover_24h')):<12}")


def cmd_audit(args):
    """Security audit for a token."""
    result = request("/bgw-pro/market/v3/coin/security/audits",
                     {"list": [{"chain": args.chain, "contract": args.contract}], "source": "bg"})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    audits = result.get("data", {}).get("list", [])
    if not audits:
        print("No audit data available.")
        return
    audit = audits[0]
    risk = audit.get("risk_level", "unknown")
    emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk, "⚪")
    print(f"\n{emoji} Security Audit: {audit.get('symbol', '?')} ({risk.upper()} risk)")
    print(f"{'Chain:':<20} {args.chain}")
    print(f"{'Contract:':<20} {args.contract}")
    items = audit.get("audit_items") or audit.get("auditItems") or []
    if items:
        print(f"\n{'Check':<30} {'Result':<10}")
        print("-" * 42)
        for item in items:
            name = item.get("name") or item.get("audit_name", "?")
            passed = item.get("result") or item.get("audit_result", "?")
            icon = "✅" if str(passed).lower() in ("pass", "true", "1") else "❌"
            print(f"{icon} {name:<28} {passed}")


def cmd_kline(args):
    """Get K-line data."""
    result = request("/bgw-pro/market/v3/coin/getKline",
                     {"chain": args.chain, "contract": args.contract,
                      "period": args.period, "size": args.size})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    candles = result.get("data", {}).get("list", [])
    if not candles:
        print("No kline data.")
        return
    print(f"\n{'Time':<22} {'Open':<14} {'High':<14} {'Low':<14} {'Close':<14} {'Volume':<14}")
    print("-" * 94)
    for c in candles[-args.size:]:
        from datetime import datetime
        ts = int(c.get("time", 0)) / 1000
        t = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "?"
        print(f"{t:<22} {fmt_price(c.get('open')):<14} {fmt_price(c.get('high')):<14} "
              f"{fmt_price(c.get('low')):<14} {fmt_price(c.get('close')):<14} "
              f"{fmt_volume(c.get('volume')):<14}")


def cmd_tx(args):
    """Get transaction stats."""
    result = request("/bgw-pro/market/v3/coin/getTxInfo",
                     {"chain": args.chain, "contract": args.contract})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    print(f"\nTransaction Stats: {args.chain}:{args.contract}")
    for period in ["5m", "1h", "4h", "24h"]:
        p = data.get(period, {})
        if p:
            print(f"\n  {period}:")
            print(f"    Buy Volume:  {fmt_volume(p.get('buyVolume'))}")
            print(f"    Sell Volume: {fmt_volume(p.get('sellVolume'))}")
            print(f"    Buyers:      {fmt_number(p.get('buyers'))}")
            print(f"    Sellers:     {fmt_number(p.get('sellers'))}")


def cmd_swap(args):
    """Get swap quote."""
    body = {
        "fromChain": args.from_chain,
        "fromContract": args.from_contract or "",
        "toChain": args.to_chain or args.from_chain,
        "toContract": args.to_contract,
        "fromAmount": args.amount,
        "estimateGas": True,
    }
    result = request("/bgw-pro/swapx/pro/quote", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    if not data:
        print("No quote available.", file=sys.stderr)
        sys.exit(1)
    print(f"\n💱 Swap Quote")
    print(f"{'From:':<16} {args.amount} ({args.from_chain})")
    print(f"{'To:':<16} {data.get('toAmount', '?')} ({args.to_chain or args.from_chain})")
    print(f"{'Market:':<16} {data.get('market', '?')}")
    print(f"{'Slippage:':<16} {data.get('slippage', '?')}%")
    print(f"{'Gas Limit:':<16} {data.get('gasLimit', '?')}")


def cmd_liquidity(args):
    """Get liquidity pools."""
    result = request("/bgw-pro/market/v3/poolList",
                     {"chain": args.chain, "contract": args.contract})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    pools = result.get("data", {}).get("list", [])
    if not pools:
        print("No liquidity pools found.")
        return
    print(f"\n{'Pool':<30} {'Liquidity':<16} {'Volume 24h':<16}")
    print("-" * 64)
    for p in pools[:10]:
        name = p.get("name") or p.get("poolName", "?")
        liq = fmt_volume(p.get("liquidity"))
        vol = fmt_volume(p.get("volume_24h") or p.get("volume24h"))
        print(f"{name:<30} {liq:<16} {vol:<16}")


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="bgw",
        description="Bitget Wallet CLI — on-chain data at your fingertips",
    )
    parser.add_argument("-V", "--version", action="version", version=f"bgw {__version__}")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    # price
    p = sub.add_parser("price", help="Get token price")
    p.add_argument("chain", help="Chain (eth, sol, bnb, base, arbitrum, trx, ton, sui, optimism)")
    p.add_argument("contract", nargs="?", default="", help="Contract address (omit for native)")
    p.set_defaults(func=cmd_price)

    # info
    p = sub.add_parser("info", help="Get detailed token info")
    p.add_argument("chain")
    p.add_argument("contract", nargs="?", default="")
    p.set_defaults(func=cmd_info)

    # top
    p = sub.add_parser("top", help="Top gainers or losers")
    p.add_argument("type", choices=["gainers", "losers"], default="gainers", nargs="?")
    p.add_argument("-n", "--limit", type=int, default=10, help="Number of results")
    p.set_defaults(func=cmd_top)

    # audit
    p = sub.add_parser("audit", help="Security audit for a token")
    p.add_argument("chain")
    p.add_argument("contract")
    p.set_defaults(func=cmd_audit)

    # kline
    p = sub.add_parser("kline", help="Get K-line (candlestick) data")
    p.add_argument("chain")
    p.add_argument("contract")
    p.add_argument("-p", "--period", default="1h", help="Period (1s,1m,5m,15m,30m,1h,4h,1d,1w)")
    p.add_argument("-n", "--size", type=int, default=24, help="Number of candles")
    p.set_defaults(func=cmd_kline)

    # tx
    p = sub.add_parser("tx", help="Transaction volume stats")
    p.add_argument("chain")
    p.add_argument("contract")
    p.set_defaults(func=cmd_tx)

    # swap
    p = sub.add_parser("swap", help="Get swap quote")
    p.add_argument("--from-chain", required=True, help="Source chain")
    p.add_argument("--from-contract", default="", help="Source token (omit for native)")
    p.add_argument("--to-chain", default="", help="Dest chain (default: same)")
    p.add_argument("--to-contract", required=True, help="Dest token contract")
    p.add_argument("--amount", required=True, help="Amount to swap")
    p.set_defaults(func=cmd_swap)

    # liquidity
    p = sub.add_parser("lp", help="Liquidity pool info")
    p.add_argument("chain")
    p.add_argument("contract")
    p.set_defaults(func=cmd_liquidity)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
