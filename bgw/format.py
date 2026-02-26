"""Output formatting helpers."""


def fmt_price(price) -> str:
    """Format price with appropriate precision."""
    if price is None:
        return "N/A"
    p = float(price)
    if p >= 1:
        return f"${p:,.2f}"
    elif p >= 0.01:
        return f"${p:.4f}"
    elif p >= 0.0001:
        return f"${p:.6f}"
    else:
        return f"${p:.10f}"


def fmt_volume(vol) -> str:
    """Format large numbers with K/M/B suffixes."""
    if vol is None:
        return "N/A"
    v = float(vol)
    if v >= 1_000_000_000:
        return f"${v / 1_000_000_000:.2f}B"
    elif v >= 1_000_000:
        return f"${v / 1_000_000:.2f}M"
    elif v >= 1_000:
        return f"${v / 1_000:.2f}K"
    else:
        return f"${v:.2f}"


def fmt_change(change) -> str:
    """Format percentage change with color indicator."""
    if change is None:
        return "N/A"
    c = float(change)
    sign = "+" if c >= 0 else ""
    arrow = "🟢" if c >= 0 else "🔴"
    return f"{arrow} {sign}{c:.2f}%"


def fmt_number(n) -> str:
    if n is None:
        return "N/A"
    return f"{float(n):,.0f}"
