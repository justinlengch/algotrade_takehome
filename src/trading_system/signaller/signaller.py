from __future__ import annotations

from typing import Iterable

import pandas as pd

from trading_system.screener.indicators import add_indicators


def signal_symbol(symbol: str, df: pd.DataFrame) -> dict:
    """Evaluate a single symbol against signaller rules."""
    latest = df.iloc[-1]
    reasons: list[str] = []

    prior_window = df.tail(64).iloc[:-1]
    if len(prior_window) < 63:
        reasons.append("insufficient_history")
        return {
            "symbol": symbol,
            "signal": False,
            "reasons": ",".join(reasons),
            "entry_price": None,
            "peak_63": None,
            "retracement": None,
        }

    if latest["pct_change_63"] < 0.30:
        reasons.append("riser_below_30pct")

    peak_high = float(prior_window["High"].max())
    peak_pos = prior_window["High"].values.argmax()
    consolidation = prior_window.iloc[peak_pos + 1 :]
    consolidation_days = len(consolidation)

    if consolidation_days < 4 or consolidation_days > 40:
        reasons.append("tread_window_outside_range")

    retracement = None
    if consolidation_days >= 1:
        trough = float(consolidation["Low"].min())
        retracement = (peak_high - trough) / peak_high if peak_high else 1.0
        if retracement >= 0.25:
            reasons.append("tread_retracement_too_large")

    if latest["Close"] <= peak_high:
        reasons.append("no_breakout")

    signal = not reasons
    return {
        "symbol": symbol,
        "signal": signal,
        "reasons": ",".join(reasons) if reasons else "",
        "entry_price": float(latest["Close"]) if signal else None,
        "peak_63": peak_high,
        "retracement": float(retracement) if retracement is not None else None,
    }


def run_signaller(data: pd.DataFrame, universe: Iterable[str]) -> pd.DataFrame:
    """Run signaller across the universe and return results."""
    results = []
    symbols = data.columns.get_level_values(0)

    for symbol in universe:
        if symbol not in symbols:
            continue
        ohlcv = data[symbol].dropna()
        if ohlcv.empty:
            continue
        enriched = add_indicators(ohlcv)
        results.append(signal_symbol(symbol, enriched))

    return pd.DataFrame(results)
