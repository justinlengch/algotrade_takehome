from __future__ import annotations

from typing import Iterable

import pandas as pd

from trading_system.screener.indicators import add_indicators


def screen_symbol(symbol: str, df: pd.DataFrame) -> dict:
    """Evaluate a single symbol against screener rules."""
    latest = df.iloc[-1]
    reasons: list[str] = []

    if latest["Close"] < 3.0:
        reasons.append("price_below_min")

    if latest["avgvol50"] < 300_000:
        reasons.append("volume_below_min")

    if latest["Close"] <= latest["sma50"]:
        reasons.append("below_sma50")

    return {
        "symbol": symbol,
        "passed": not reasons,
        "reasons": ",".join(reasons) if reasons else "",
        "close": float(latest["Close"]),
        "avgvol50": float(latest["avgvol50"]),
        "sma50": float(latest["sma50"]),
    }


def run_screener(data: pd.DataFrame, universe: Iterable[str]) -> pd.DataFrame:
    """Run screener across the universe and return results."""
    results = []
    symbols = data.columns.get_level_values(0)

    for symbol in universe:
        if symbol not in symbols:
            continue
        ohlcv = data[symbol].dropna()
        if ohlcv.empty:
            continue
        enriched = add_indicators(ohlcv)
        results.append(screen_symbol(symbol, enriched))

    return pd.DataFrame(results)
