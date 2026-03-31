"""Bitget Wallet CLI — on-chain data at your fingertips."""
from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .api import request
from .format import fmt_change, fmt_number, fmt_price, fmt_volume

CHAINS = {
    "eth": "1", "sol": "100278", "bnb": "56", "base": "8453",
    "arbitrum": "42161", "trx": "6", "ton": "100280",
    "suinet": "100281", "optimism": "10", "matic": "137",
    "morph": "morph",
}


def _get_token(chain: str, contract: str) -> dict | None:
    result = request("/market/v3/coin/batchGetBaseInfo",
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
    """Get top ranked tokens (topGainers, topLosers, Hotpicks, etc.)."""
    result = request("/market/v3/topRank/detail", {"name": args.name})
    items = result.get("data", {}).get("list", [])
    if args.json:
        print(json.dumps(items[:args.limit], indent=2))
    else:
        print(f"\n📊 {args.name}")
        print(f"{'#':<4} {'Symbol':<12} {'Price':<16} {'24h Change':<14} {'Volume':<12}")
        print("-" * 60)
        for i, t in enumerate(items[:args.limit], 1):
            print(f"{i:<4} {t.get('symbol', '?'):<12} {fmt_price(t.get('price')):<16} "
                  f"{fmt_change(t.get('change_24h')):<14} {fmt_volume(t.get('turnover_24h')):<12}")


def cmd_audit(args):
    """Security audit for a token."""
    result = request("/market/v3/coin/security/audits",
                     {"list": [{"chain": args.chain, "contract": args.contract}], "source": "bg"})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", [])
    audits = data.get("list", []) if isinstance(data, dict) else data if isinstance(data, list) else []
    if not audits:
        print("No audit data available.")
        return
    audit = audits[0]
    risk = audit.get("risk_level", "")
    if not risk:
        if audit.get("highRisk"):
            risk = "high"
        elif audit.get("riskCount", 0) > 0:
            risk = "high"
        elif audit.get("warnCount", 0) > 0:
            risk = "medium"
        else:
            risk = "low"
    emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk, "⚪")
    symbol = audit.get("symbol") or audit.get("contract", "?")[:12]
    print(f"\n{emoji} Security Audit: {symbol} ({risk.upper()} risk)")
    print(f"{'Chain:':<20} {args.chain}")
    print(f"{'Contract:':<20} {args.contract}")
    buy_tax = audit.get("buyTax", 0)
    sell_tax = audit.get("sellTax", 0)
    print(f"{'Buy Tax:':<20} {buy_tax}%")
    print(f"{'Sell Tax:':<20} {sell_tax}%")
    flags = [
        ("Freeze Authority", audit.get("freezeAuth")),
        ("Mint Authority", audit.get("mintAuth")),
        ("Token2022", audit.get("token2022")),
        ("LP Locked", audit.get("lpLock")),
    ]
    flag_items = [(n, v) for n, v in flags if v is not None]
    if flag_items:
        print(f"\n{'Flag':<25} {'Status':<10}")
        print("-" * 37)
        for name, val in flag_items:
            if name == "LP Locked":
                icon = "✅" if val else "⚠️"
            else:
                icon = "⚠️" if val else "✅"
            print(f"{icon} {name:<23} {val}")
    for check_key, label in [("riskChecks", "🔴 Risk"), ("warnChecks", "⚠️ Warn"), ("lowChecks", "ℹ️ Info")]:
        checks = audit.get(check_key)
        if checks:
            print(f"\n{label} Checks:")
            for item in checks:
                name = item.get("name") or item.get("labelName") or item.get("audit_name", "?")
                print(f"  - {name}")
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
    result = request("/market/v3/coin/getKline",
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
    result = request("/market/v3/coin/getTxInfo",
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


def cmd_batch_tx(args):
    """Batch get transaction stats for multiple tokens."""
    tokens = []
    for item in args.tokens:
        chain, contract = item.split(":", 1)
        tokens.append({"chain": chain, "contract": contract})
    result = request("/market/v3/coin/batchGetTxInfo", {"list": tokens})
    print(json.dumps(result, indent=2))


def cmd_history(args):
    """Get historical token list by timestamp."""
    result = request("/market/v3/historical-coins",
                     {"createTime": args.create_time, "limit": args.limit})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    tokens = data.get("tokenList", []) if isinstance(data, dict) else data if isinstance(data, list) else []
    if not tokens:
        print("No tokens found.")
        return
    print(f"\n{'Symbol':<12} {'Chain':<8} {'Name':<30} {'Created'}")
    print("-" * 70)
    for t in tokens[:args.limit]:
        print(f"{t.get('symbol', '?'):<12} {t.get('chain', '?'):<8} {t.get('name', '?'):<30} {t.get('createTime', '?')}")


def cmd_batch_price(args):
    """Batch get token info for multiple tokens."""
    tokens = []
    for item in args.tokens:
        chain, contract = item.split(":", 1)
        tokens.append({"chain": chain, "contract": contract})
    result = request("/market/v3/coin/batchGetBaseInfo", {"list": tokens})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    items = result.get("data", {}).get("list", [])
    if not items:
        print("No token data returned.")
        return
    print(f"\n{'Symbol':<12} {'Price':<16} {'24h Change':<14} {'Chain'}")
    print("-" * 56)
    for t in items:
        print(f"{t.get('symbol', '?'):<12} {fmt_price(t.get('price')):<16} "
              f"{fmt_change(t.get('change_24h')):<14} {t.get('chain', '?')}")


def cmd_liquidity(args):
    """Get liquidity pools."""
    result = request("/market/v3/poolList",
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


def cmd_search(args):
    """Search for tokens by keyword."""
    body = {"keyword": args.keyword, "limit": args.limit}
    if args.chain:
        body["chain"] = args.chain
    if args.order_by:
        body["orderBy"] = args.order_by
    result = request("/market/v3/coin/search", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    items = result.get("data", {}).get("list", [])
    if not items:
        print("No tokens found.")
        return
    print(f"\n{'Symbol':<12} {'Name':<20} {'Chain':<10} {'Contract':<44} {'Price'}")
    print("-" * 100)
    for t in items[:args.limit]:
        symbol = t.get("symbol", "?")
        name = t.get("name", "?")[:18]
        chain = t.get("chain", "?")
        contract = t.get("contract", "")[:42]
        price = fmt_price(t.get("price"))
        print(f"{symbol:<12} {name:<20} {chain:<10} {contract:<44} {price}")


def cmd_market(args):
    """Get market info for a token."""
    result = request("/market/v3/coin/getMarketInfo",
                     {"chain": args.chain, "contract": args.contract})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    if not data:
        print("No market data available.")
        return
    print(f"\n📊 Market Info: {args.chain}:{args.contract}")
    print(f"{'Price:':<20} {fmt_price(data.get('price'))}")
    print(f"{'Market Cap:':<20} {fmt_volume(data.get('marketCap') or data.get('market_cap'))}")
    print(f"{'FDV:':<20} {fmt_volume(data.get('fdv') or data.get('fullyDilutedValuation'))}")
    print(f"{'Liquidity:':<20} {fmt_volume(data.get('liquidity'))}")
    print(f"{'Holders:':<20} {fmt_number(data.get('holders'))}")
    print(f"{'24h Change:':<20} {fmt_change(data.get('change_24h') or data.get('change24h'))}")
    narratives = data.get("narratives") or data.get("tags") or []
    if narratives:
        tags = ", ".join(narratives) if isinstance(narratives, list) else str(narratives)
        print(f"{'Narratives:':<20} {tags}")


def cmd_dev(args):
    """Get developer activity and rug rate analysis."""
    body = {"chain": args.chain, "contract": args.contract, "limit": args.limit}
    if args.migrated is not None:
        body["migrated"] = args.migrated
    result = request("/market/v3/coin/dev", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    if not data:
        print("No developer data available.")
        return
    summary = data.get("summary") or data
    rug_rate = summary.get("rugRate") or summary.get("rug_rate")
    total = summary.get("totalProjects") or summary.get("total")
    if rug_rate is not None:
        print(f"\n🔍 Developer Analysis: {args.chain}:{args.contract}")
        print(f"{'Rug Rate:':<20} {rug_rate}%")
    if total is not None:
        print(f"{'Total Projects:':<20} {total}")
    projects = data.get("list") or data.get("projects") or []
    if projects:
        print(f"\n{'Symbol':<12} {'Chain':<10} {'Status':<12} {'MC':<14} {'Created'}")
        print("-" * 64)
        for p in projects[:args.limit]:
            symbol = p.get("symbol", "?")
            chain = p.get("chain", "?")
            status = p.get("status", "?")
            mc = fmt_volume(p.get("marketCap") or p.get("market_cap"))
            created = p.get("createTime") or p.get("created", "?")
            print(f"{symbol:<12} {chain:<10} {status:<12} {mc:<14} {created}")


def cmd_launchpad(args):
    """Get launchpad token listings."""
    body = {"chain": args.chain, "limit": args.limit}
    if args.platforms:
        body["platforms"] = args.platforms
    if args.stage:
        body["stage"] = args.stage
    if args.mc_min is not None:
        body["mcMin"] = args.mc_min
    if args.mc_max is not None:
        body["mcMax"] = args.mc_max
    if args.holder_min is not None:
        body["holderMin"] = args.holder_min
    if args.holder_max is not None:
        body["holderMax"] = args.holder_max
    if args.lp_min is not None:
        body["lpMin"] = args.lp_min
    if args.lp_max is not None:
        body["lpMax"] = args.lp_max
    if args.keywords:
        body["keywords"] = args.keywords
    result = request("/market/v3/launchpad/tokens", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    items = result.get("data", {}).get("list", [])
    if not items:
        print("No launchpad tokens found.")
        return
    print(f"\n🚀 Launchpad Tokens")
    print(f"{'Symbol':<12} {'MC':<14} {'Holders':<10} {'LP':<14} {'Progress':<12} {'Platform'}")
    print("-" * 78)
    for t in items[:args.limit]:
        symbol = t.get("symbol", "?")
        mc = fmt_volume(t.get("marketCap") or t.get("market_cap"))
        holders = fmt_number(t.get("holders"))
        lp = fmt_volume(t.get("liquidity") or t.get("lp"))
        progress = t.get("progress", "?")
        if isinstance(progress, (int, float)):
            progress = f"{progress:.1f}%"
        platform = t.get("platform", "?")
        print(f"{symbol:<12} {mc:<14} {holders:<10} {lp:<14} {progress:<12} {platform}")


def cmd_smart_kline(args):
    """Get simplified K-line with hot level."""
    body = {"chain": args.chain, "contract": args.contract, "period": args.period}
    if args.size:
        body["size"] = args.size
    result = request("/market/v2/coin/SimpleKline", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    if not data:
        print("No kline data.")
        return
    hot_level = data.get("hotLevel") or data.get("hot_level")
    if hot_level is not None:
        print(f"\n🔥 Hot Level: {hot_level}")
    candles = data.get("list") or data.get("klines") or []
    if candles:
        print(f"\n{'Time':<22} {'Open':<14} {'High':<14} {'Low':<14} {'Close':<14} {'Volume':<14}")
        print("-" * 94)
        from datetime import datetime
        for c in candles[-10:]:
            ts = int(c.get("time", 0))
            if ts > 1e12:
                ts = ts / 1000
            t = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "?"
            print(f"{t:<22} {fmt_price(c.get('open')):<14} {fmt_price(c.get('high')):<14} "
                  f"{fmt_price(c.get('low')):<14} {fmt_price(c.get('close')):<14} "
                  f"{fmt_volume(c.get('volume')):<14}")


def cmd_dynamics(args):
    """Get trading dynamics across time windows."""
    result = request("/market/v2/coin/GetTradingDynamics",
                     {"chain": args.chain, "contract": args.contract})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    if not data:
        print("No trading dynamics data.")
        return
    print(f"\n📈 Trading Dynamics: {args.chain}:{args.contract}")
    for period in ["5m", "1h", "4h", "24h"]:
        p = data.get(period, {})
        if p:
            print(f"\n  {period}:")
            print(f"    Buy Volume:    {fmt_volume(p.get('buyVolume') or p.get('buy_volume'))}")
            print(f"    Sell Volume:   {fmt_volume(p.get('sellVolume') or p.get('sell_volume'))}")
            print(f"    Buyers:        {fmt_number(p.get('buyers'))}")
            print(f"    Sellers:       {fmt_number(p.get('sellers'))}")
            print(f"    Price Change:  {fmt_change(p.get('priceChange') or p.get('price_change'))}")
    if isinstance(data, list):
        for item in data:
            period = item.get("period", "?")
            print(f"\n  {period}:")
            print(f"    Buy Volume:    {fmt_volume(item.get('buyVolume'))}")
            print(f"    Sell Volume:   {fmt_volume(item.get('sellVolume'))}")
            print(f"    Buyers:        {fmt_number(item.get('buyers'))}")
            print(f"    Sellers:       {fmt_number(item.get('sellers'))}")


def cmd_txlist(args):
    """Get transaction list for a token."""
    body = {
        "chain": args.chain,
        "contract": args.contract,
        "page": args.page,
        "size": args.size,
    }
    if args.side:
        body["side"] = args.side
    if args.period:
        body["period"] = args.period
    if args.tags:
        body["tags"] = args.tags
    result = request("/market/v2/coin/TransactionList", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    items = result.get("data", {}).get("list", [])
    if not items:
        print("No transactions found.")
        return
    print(f"\n{'Time':<20} {'Side':<6} {'Amount':<16} {'Price':<16} {'Address'}")
    print("-" * 80)
    from datetime import datetime
    for tx in items[:args.size]:
        ts = int(tx.get("time", 0))
        if ts > 1e12:
            ts = ts / 1000
        t = datetime.fromtimestamp(ts).strftime("%m-%d %H:%M") if ts else "?"
        side = tx.get("side", "?")
        icon = "🟢" if side.lower() == "buy" else "🔴"
        amount = fmt_volume(tx.get("amount") or tx.get("tokenAmount"))
        price = fmt_price(tx.get("price"))
        addr = (tx.get("address") or tx.get("maker", "?"))[:16]
        print(f"{t:<20} {icon} {side:<4} {amount:<16} {price:<16} {addr}")


def cmd_holders(args):
    """Get holder distribution and top holders."""
    body = {"chain": args.chain, "contract": args.contract, "sort": args.sort}
    if args.special:
        body["special"] = args.special
    result = request("/market/v2/GetHoldersInfo", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    if not data:
        print("No holder data available.")
        return
    print(f"\n👥 Holder Info: {args.chain}:{args.contract}")
    holder_count = data.get("holderCount") or data.get("holder_count")
    top10_pct = data.get("top10Percent") or data.get("top10_percent")
    if holder_count is not None:
        print(f"{'Total Holders:':<20} {fmt_number(holder_count)}")
    if top10_pct is not None:
        print(f"{'Top 10 Hold %:':<20} {top10_pct}%")
    holders_raw = data.get("holders", {})
    holders = holders_raw.get("list", []) if isinstance(holders_raw, dict) else holders_raw if isinstance(holders_raw, list) else []
    if not holders:
        holders = data.get("list", [])
    if holders:
        print(f"\n{'#':<4} {'Address':<44} {'Holding %':<12} {'Amount'}")
        print("-" * 76)
        for i, h in enumerate(holders[:20], 1):
            addr = (h.get("addr") or h.get("address") or "?")[:42]
            pct = h.get("percent") or h.get("holdingPercent") or "?"
            amount = fmt_volume(h.get("amount") or h.get("balance"))
            print(f"{i:<4} {addr:<44} {pct:<12} {amount}")


def cmd_profit(args):
    """Get profit address analysis."""
    result = request("/market/v2/coin/GetProfitAddressAnalysis",
                     {"chain": args.chain, "contract": args.contract})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    if not data:
        print("No profit data available.")
        return
    print(f"\n💰 Profit Analysis: {args.chain}:{args.contract}")
    for key, label in [
        ("profitCount", "Profitable Addresses"),
        ("lossCount", "Loss Addresses"),
        ("profitPercent", "Profit %"),
        ("avgProfit", "Avg Profit"),
        ("avgLoss", "Avg Loss"),
        ("totalProfit", "Total Profit"),
        ("totalLoss", "Total Loss"),
    ]:
        val = data.get(key)
        if val is None:
            snake = "".join(f"_{c.lower()}" if c.isupper() else c for c in key)
            val = data.get(snake)
        if val is not None:
            if "percent" in key.lower() or "Percent" in key:
                print(f"  {label:<26} {val}%")
            elif "count" in key.lower() or "Count" in key:
                print(f"  {label:<26} {fmt_number(val)}")
            else:
                print(f"  {label:<26} {fmt_volume(val)}")


def cmd_top_profit(args):
    """Get top profitable addresses for a token."""
    result = request("/market/v2/coin/GetTopProfit",
                     {"chain": args.chain, "contract": args.contract})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    items = result.get("data", {}).get("list", [])
    if not items:
        items = result.get("data", []) if isinstance(result.get("data"), list) else []
    if not items:
        print("No top profit data available.")
        return
    print(f"\n🏆 Top Profitable Addresses: {args.chain}:{args.contract}")
    print(f"{'#':<4} {'Address':<44} {'Profit':<16} {'ROI'}")
    print("-" * 76)
    for i, a in enumerate(items[:20], 1):
        addr = (a.get("address") or "?")[:42]
        profit = fmt_volume(a.get("profit") or a.get("realizedProfit"))
        roi = a.get("roi") or a.get("profitPercent") or "?"
        if isinstance(roi, (int, float)):
            roi = f"{roi:.1f}%"
        print(f"{i:<4} {addr:<44} {profit:<16} {roi}")


# ── Swap Flow Commands ────────────────────────────────────────────────────

def cmd_quote(args):
    """Get swap quote (first step — returns multiple markets)."""
    body = {
        "fromAddress": args.from_address,
        "fromChain": args.from_chain,
        "fromSymbol": args.from_symbol,
        "fromContract": args.from_contract or "",
        "fromAmount": args.from_amount,
        "toChain": args.to_chain or args.from_chain,
        "toSymbol": args.to_symbol,
        "toContract": args.to_contract or "",
        "tab_type": "swap",
        "publicKey": "",
        "slippage": str(args.slippage) if args.slippage else "",
        "toAddress": args.to_address or args.from_address,
    }
    result = request("/swap-go/swapx/quote", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    if not data:
        print(f"No quote available: {result.get('msg', 'unknown error')}", file=sys.stderr)
        sys.exit(1)
    print(f"\n💱 Swap Quote")
    markets = data.get("quoteResults") or data.get("markets") or data.get("list") or []
    if isinstance(data, dict) and not markets:
        # Single market response
        print(f"{'From:':<16} {args.from_amount} {args.from_symbol} ({args.from_chain})")
        print(f"{'To:':<16} {data.get('toAmount', '?')} {args.to_symbol} ({args.to_chain or args.from_chain})")
        print(f"{'Market:':<16} {data.get('market', '?')}")
    else:
        print(f"{'From:':<16} {args.from_amount} {args.from_symbol} ({args.from_chain})")
        print(f"{'To Chain:':<16} {args.to_chain or args.from_chain}")
        print(f"\n{'#':<4} {'Market':<24} {'Out Amount':<16} {'Slippage':<10} {'Features'}")
        print("-" * 74)
        for i, m in enumerate(markets, 1):
            mkt = m.get("market", {})
            market_name = mkt.get("label", mkt.get("id", str(mkt))) if isinstance(mkt, dict) else str(mkt)
            protocol = mkt.get("protocol", "") if isinstance(mkt, dict) else ""
            to_amt = str(m.get("outAmount") or m.get("toAmount", "?"))
            slip_info = m.get("slippageInfo", {})
            slip = str(slip_info.get("slippage", "?")) if isinstance(slip_info, dict) else str(m.get("slippage", "?"))
            features = ",".join(m.get("features", []))
            print(f"{i:<4} {market_name:<24} {to_amt:<16} {slip:<10} {features}")


def cmd_confirm(args):
    """Confirm swap with chosen market (second quote)."""
    body = {
        "fromChain": args.from_chain,
        "fromSymbol": args.from_symbol,
        "fromContract": args.from_contract or "",
        "fromAmount": args.from_amount,
        "fromAddress": args.from_address,
        "toChain": args.to_chain or args.from_chain,
        "toSymbol": args.to_symbol,
        "toContract": args.to_contract or "",
        "toAddress": args.to_address or args.from_address,
        "market": args.market,
        "slippage": str(args.slippage) if args.slippage else "1",
        "gasLevel": args.gas_level,
        "features": [args.feature] if args.feature else ["user_gas"],
        "protocol": args.protocol,
    }
    result = request("/swap-go/swapx/confirm", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    if not data:
        print(f"Confirm failed: {result.get('msg', 'unknown error')}", file=sys.stderr)
        sys.exit(1)
    print(f"\n✅ Swap Confirmed")
    print(f"{'From:':<16} {args.from_amount} {args.from_symbol} ({args.from_chain})")
    qr = data.get("quoteResult", {})
    print(f"{'Out Amount:':<16} {qr.get('outAmount', data.get('toAmount', '?'))}")
    print(f"{'Min Amount:':<16} {qr.get('minAmount', '?')}")
    print(f"{'Gas Total:':<16} {qr.get('gasTotalAmount', data.get('gasLimit', '?'))}")
    print(f"{'Market:':<16} {args.market}")
    print(f"{'Order ID:':<16} {data.get('orderId', '?')}")


def cmd_make_order(args):
    """Create swap order (returns unsigned tx data)."""
    body = {
        "orderId": args.order_id,
        "fromChain": args.from_chain,
        "fromContract": args.from_contract or "",
        "fromSymbol": args.from_symbol,
        "fromAddress": args.from_address,
        "toChain": args.to_chain or args.from_chain,
        "toContract": args.to_contract or "",
        "toSymbol": args.to_symbol,
        "toAddress": args.to_address or args.from_address,
        "fromAmount": args.from_amount,
        "slippage": str(args.slippage) if args.slippage else "1",
        "market": args.market,
        "protocol": args.protocol,
        "source": "agent",
    }
    result = request("/swap-go/swapx/makeOrder", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    if not data:
        print(f"Make order failed: {result.get('msg', 'unknown error')}", file=sys.stderr)
        sys.exit(1)
    print(f"\n📝 Order Created")
    print(f"{'Order ID:':<16} {args.order_id}")
    txs = data.get("txs", [])
    print(f"{'Transactions:':<16} {len(txs)}")
    for i, tx in enumerate(txs):
        print(f"  [{i}] to={tx.get('to', '?')[:20]}... value={tx.get('value', '0')}")


def cmd_send_order(args):
    """Submit signed order transactions."""
    txs = json.loads(args.txs)
    body = {
        "orderId": args.order_id,
        "txs": txs,
    }
    result = request("/swap-go/swapx/send", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    if result.get("status") == 0:
        print(f"✅ Order {args.order_id} submitted successfully")
    else:
        print(f"❌ Submit failed: {result.get('msg', 'unknown error')}", file=sys.stderr)


def cmd_order_details(args):
    """Query order status."""
    result = request("/swap-go/swapx/getOrderDetails", {"orderId": args.order_id})
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    if not data:
        print(f"Query failed: {result.get('msg', 'unknown error')}", file=sys.stderr)
        sys.exit(1)
    status = data.get("status", "?")
    icon = {"success": "✅", "failed": "❌", "processing": "⏳", "init": "📝"}.get(status, "❓")
    print(f"\n{icon} Order Status: {status}")
    print(f"{'Order ID:':<16} {data.get('orderId', '?')}")
    print(f"{'From:':<16} {data.get('fromAmount', '?')} ({data.get('fromChain', '?')})")
    print(f"{'To:':<16} {data.get('toAmount', '?')} ({data.get('toChain', '?')})")


def cmd_check_token(args):
    """Pre-trade token risk check."""
    body = {"list": [{"chain": args.chain, "contract": args.contract, "symbol": args.symbol or ""}]}
    result = request("/swap-go/swapx/checkSwapToken", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    data = result.get("data", {})
    check_list = data.get("list", []) if isinstance(data, dict) else []
    if not check_list:
        print(f"✅ No risks detected for {args.chain}:{args.contract}")
        return
    for item in check_list:
        token_checks = item.get("checkTokenList", [])
        if not token_checks:
            print(f"✅ {item.get('symbol', '?')}: No risks")
        else:
            for c in token_checks:
                print(f"⚠️ {c.get('waringType', '?')}: {c.get('desc', '')}")


def cmd_token_list(args):
    """Get popular swap token list."""
    body = {"chain": args.chain}
    result = request("/swap-go/swapx/getTokenList", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    items = result.get("data", {}).get("list", [])
    if not items:
        items = result.get("data", []) if isinstance(result.get("data"), list) else []
    if not items:
        print("No tokens found.")
        return
    print(f"\n{'Symbol':<12} {'Name':<20} {'Contract':<44}")
    print("-" * 78)
    for t in items[:30]:
        symbol = t.get("symbol", "?")
        name = t.get("name", "?")[:18]
        contract = t.get("contract", "")[:42]
        print(f"{symbol:<12} {name:<20} {contract:<44}")


def cmd_balance(args):
    """Get wallet token balances."""
    contracts = args.contract if args.contract else [""]
    body = {
        "list": [{"chain": args.chain, "address": args.address, "contract": contracts}],
        "nocache": True,
        "appointCurrency": "usd",
        "noreport": True,
    }
    result = request("/user/wallet/batchV2", body)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    raw = result.get("data", [])
    # data is array of {chain, address, list: {"": {...}, "0x...": {...}}}
    items = []
    if isinstance(raw, list):
        for entry in raw:
            token_map = entry.get("list", {})
            if isinstance(token_map, dict):
                for contract_addr, info in token_map.items():
                    if isinstance(info, dict):
                        info["_contract"] = contract_addr
                        items.append(info)
            elif isinstance(token_map, list):
                items.extend(token_map)
    elif isinstance(raw, dict):
        items = raw.get("list", [])
    if not items:
        print("No balance data.")
        return
    print(f"\n💰 Balances: {args.chain} — {args.address[:16]}...")
    print(f"{'Symbol':<12} {'Balance':<20} {'Value (USD)':<16}")
    print("-" * 50)
    for t in items:
        symbol = t.get("coin") or t.get("symbol") or t.get("tokenSymbol") or t.get("name", "?")
        balance = t.get("balance") or t.get("amount", "0")
        price = t.get("price", "")
        usd_val = ""
        try:
            if balance and price and float(balance) > 0:
                usd_val = f"${float(balance) * float(price):,.2f}"
        except (ValueError, TypeError):
            pass
        if float(balance or 0) == 0:
            continue  # skip zero balances
        print(f"{symbol:<12} {str(balance):<20} {usd_val:<16}")


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
    p = sub.add_parser("top", help="Top ranked tokens (topGainers, topLosers, Hotpicks)")
    p.add_argument("name", help="Rank name (e.g. topGainers, topLosers, Hotpicks)")
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

    # batch-tx
    p = sub.add_parser("batch-tx", help="Batch transaction stats for multiple tokens")
    p.add_argument("tokens", nargs="+", help="chain:contract pairs (e.g. sol:EPjF... eth:0xdAC...)")
    p.set_defaults(func=cmd_batch_tx)

    # history (historical-coins)
    p = sub.add_parser("history", help="Get historical token list by timestamp")
    p.add_argument("create_time", help="Timestamp (e.g. '2025-06-17 06:55:28')")
    p.add_argument("-n", "--limit", type=int, default=10, help="Number of records")
    p.set_defaults(func=cmd_history)

    # batch-price
    p = sub.add_parser("batch-price", help="Batch get token info for multiple tokens")
    p.add_argument("tokens", nargs="+", help="chain:contract pairs (e.g. sol: eth:0xdAC...)")
    p.set_defaults(func=cmd_batch_price)

    # liquidity
    p = sub.add_parser("lp", help="Liquidity pool info")
    p.add_argument("chain")
    p.add_argument("contract")
    p.set_defaults(func=cmd_liquidity)

    # search
    p = sub.add_parser("search", help="Search tokens by keyword")
    p.add_argument("keyword", help="Search keyword (symbol, name, contract)")
    p.add_argument("--chain", default="", help="Filter by chain")
    p.add_argument("-n", "--limit", type=int, default=20, help="Number of results")
    p.add_argument("--order-by", default="", help="Order by field")
    p.set_defaults(func=cmd_search)

    # market
    p = sub.add_parser("market", help="Get market info (price, MC, FDV, liquidity)")
    p.add_argument("chain")
    p.add_argument("contract")
    p.set_defaults(func=cmd_market)

    # dev
    p = sub.add_parser("dev", help="Developer activity and rug rate analysis")
    p.add_argument("chain")
    p.add_argument("contract")
    p.add_argument("-n", "--limit", type=int, default=30, help="Number of projects")
    p.add_argument("--migrated", action="store_true", default=None, help="Filter migrated only")
    p.set_defaults(func=cmd_dev)

    # launchpad
    p = sub.add_parser("launchpad", help="Launchpad token listings")
    p.add_argument("--chain", default="sol", help="Chain (default: sol)")
    p.add_argument("--platforms", default="", help="Platform filter")
    p.add_argument("--stage", default="", help="Stage filter")
    p.add_argument("--mc-min", type=float, default=None, help="Min market cap")
    p.add_argument("--mc-max", type=float, default=None, help="Max market cap")
    p.add_argument("--holder-min", type=int, default=None, help="Min holders")
    p.add_argument("--holder-max", type=int, default=None, help="Max holders")
    p.add_argument("--lp-min", type=float, default=None, help="Min liquidity")
    p.add_argument("--lp-max", type=float, default=None, help="Max liquidity")
    p.add_argument("--keywords", default="", help="Keyword filter")
    p.add_argument("-n", "--limit", type=int, default=20, help="Number of results")
    p.set_defaults(func=cmd_launchpad)

    # smart-kline
    p = sub.add_parser("smart-kline", help="Simplified K-line with hot level")
    p.add_argument("chain")
    p.add_argument("contract")
    p.add_argument("-p", "--period", default="5m", help="Period (1m,5m,15m,30m,1h,4h,1d)")
    p.add_argument("-n", "--size", type=int, default=None, help="Number of candles")
    p.set_defaults(func=cmd_smart_kline)

    # dynamics
    p = sub.add_parser("dynamics", help="Trading dynamics across time windows")
    p.add_argument("chain")
    p.add_argument("contract")
    p.set_defaults(func=cmd_dynamics)

    # txlist
    p = sub.add_parser("txlist", help="Transaction list for a token")
    p.add_argument("chain")
    p.add_argument("contract")
    p.add_argument("--page", type=int, default=1, help="Page number")
    p.add_argument("--size", type=int, default=20, help="Page size")
    p.add_argument("--side", default="", help="Filter by side (buy/sell)")
    p.add_argument("--period", default="", help="Time period filter")
    p.add_argument("--tags", nargs="+", default=None, help="Tag filters")
    p.set_defaults(func=cmd_txlist)

    # holders
    p = sub.add_parser("holders", help="Holder distribution and top holders")
    p.add_argument("chain")
    p.add_argument("contract")
    p.add_argument("--sort", default="holding_desc", help="Sort order (default: holding_desc)")
    p.add_argument("--special", default="", help="Special filter")
    p.set_defaults(func=cmd_holders)

    # profit
    p = sub.add_parser("profit", help="Profit address analysis")
    p.add_argument("chain")
    p.add_argument("contract")
    p.set_defaults(func=cmd_profit)

    # top-profit
    p = sub.add_parser("top-profit", help="Top profitable addresses")
    p.add_argument("chain")
    p.add_argument("contract")
    p.set_defaults(func=cmd_top_profit)

    # ── Swap Flow ─────────────────────────────────────────────────────────

    # quote
    p = sub.add_parser("quote", help="Get swap quote (multiple markets)")
    p.add_argument("--from-address", required=True, help="Sender wallet address")
    p.add_argument("--from-chain", required=True, help="Source chain")
    p.add_argument("--from-symbol", required=True, help="Source token symbol (e.g. ETH)")
    p.add_argument("--from-contract", default="", help="Source token contract (omit for native)")
    p.add_argument("--from-amount", required=True, help="Human-readable amount")
    p.add_argument("--to-chain", default="", help="Dest chain (default: same)")
    p.add_argument("--to-symbol", required=True, help="Dest token symbol (e.g. USDT)")
    p.add_argument("--to-contract", default="", help="Dest token contract (omit for native)")
    p.add_argument("--to-address", default="", help="Recipient address (default: from-address)")
    p.add_argument("--slippage", type=float, help="Slippage tolerance %")
    p.set_defaults(func=cmd_quote)

    # confirm
    p = sub.add_parser("confirm", help="Confirm swap with chosen market")
    p.add_argument("--from-chain", required=True, help="Source chain")
    p.add_argument("--from-symbol", required=True, help="Source token symbol")
    p.add_argument("--from-contract", default="", help="Source token contract")
    p.add_argument("--from-amount", required=True, help="Human-readable amount")
    p.add_argument("--from-address", required=True, help="Sender wallet address")
    p.add_argument("--to-chain", default="", help="Dest chain")
    p.add_argument("--to-symbol", required=True, help="Dest token symbol")
    p.add_argument("--to-contract", default="", help="Dest token contract")
    p.add_argument("--to-address", default="", help="Recipient address")
    p.add_argument("--market", required=True, help="Market ID from quote result")
    p.add_argument("--protocol", required=True, help="Protocol from quote result")
    p.add_argument("--slippage", type=float, help="Slippage tolerance %")
    p.add_argument("--gas-level", default="average", help="Gas level (average/fast)")
    p.add_argument("--feature", default="", help="Feature: user_gas or no_gas")
    p.set_defaults(func=cmd_confirm)

    # make-order
    p = sub.add_parser("make-order", help="Create swap order (unsigned tx data)")
    p.add_argument("--order-id", required=True, help="Order ID from confirm result")
    p.add_argument("--from-chain", required=True, help="Source chain")
    p.add_argument("--from-contract", default="", help="Source token contract")
    p.add_argument("--from-symbol", required=True, help="Source token symbol")
    p.add_argument("--from-amount", required=True, help="Human-readable amount")
    p.add_argument("--from-address", required=True, help="Sender wallet address")
    p.add_argument("--to-chain", default="", help="Dest chain")
    p.add_argument("--to-contract", default="", help="Dest token contract")
    p.add_argument("--to-symbol", required=True, help="Dest token symbol")
    p.add_argument("--to-address", default="", help="Recipient address")
    p.add_argument("--market", required=True, help="Market from confirm result")
    p.add_argument("--protocol", required=True, help="Protocol from confirm result")
    p.add_argument("--slippage", type=float, help="Slippage tolerance %")
    p.set_defaults(func=cmd_make_order)

    # send-order
    p = sub.add_parser("send-order", help="Submit signed order transactions")
    p.add_argument("--order-id", required=True, help="Order ID from make-order")
    p.add_argument("--txs", required=True, help="JSON array of txs with sig filled")
    p.set_defaults(func=cmd_send_order)

    # order-details
    p = sub.add_parser("order-details", help="Query order status")
    p.add_argument("--order-id", required=True, help="Order ID")
    p.set_defaults(func=cmd_order_details)

    # check-token
    p = sub.add_parser("check-token", help="Pre-trade token risk check")
    p.add_argument("chain")
    p.add_argument("contract")
    p.add_argument("--symbol", default="", help="Token symbol")
    p.set_defaults(func=cmd_check_token)

    # token-list
    p = sub.add_parser("token-list", help="Popular swap tokens for a chain")
    p.add_argument("chain", help="Chain (e.g. eth, sol, bnb)")
    p.set_defaults(func=cmd_token_list)

    # balance
    p = sub.add_parser("balance", help="Get wallet token balances")
    p.add_argument("chain", help="Chain (e.g. eth, sol, bnb)")
    p.add_argument("address", help="Wallet address")
    p.add_argument("--contract", action="append", default=None,
                   help="Token contract (repeatable; omit for native)")
    p.set_defaults(func=cmd_balance)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
