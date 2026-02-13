from __future__ import annotations

from typing import Iterable

import pandas as pd

from trading_system.screener.indicators import add_indicators


def execute_symbol(
    symbol: str,
    df: pd.DataFrame,
    signal_date: pd.Timestamp,
    account_equity: float = 100_000.0,
    risk_pct: float = 0.02,
) -> dict:
    """Compute entry, stop, sizing, and exit for a single symbol."""
    if signal_date not in df.index:
        return {
            "symbol": symbol,
            "valid": False,
            "reasons": "signal_date_missing",
            "entry_price": None,
            "stop_price": None,
            "stop_distance": None,
            "atr14": None,
            "risk_dollars": None,
            "position_size": None,
            "exit_trigger": False,
            "exit_price": None,
            "exit_date": None,
        }

    latest = df.loc[signal_date]
    reasons: list[str] = []

    entry_price = float(latest["Close"])
    stop_price = float(latest["Low"])
    atr14 = float(latest["atr14"]) if pd.notna(latest["atr14"]) else None

    stop_distance = entry_price - stop_price
    if stop_distance <= 0:
        reasons.append("invalid_stop_distance")

    if atr14 is None:
        reasons.append("atr_missing")
    elif stop_distance > atr14:
        reasons.append("stop_distance_gt_atr")

    risk_dollars = account_equity * risk_pct
    position_size = None
    if not reasons:
        position_size = risk_dollars / stop_distance if stop_distance > 0 else None

    future = df.loc[signal_date:]
    exit_trigger = False
    exit_price = None
    exit_date = None
    for idx, row in future.iloc[1:].iterrows():
        if pd.notna(row["sma10"]) and row["Close"] < row["sma10"]:
            exit_trigger = True
            exit_price = float(row["Close"])
            exit_date = idx
            break

    return {
        "symbol": symbol,
        "valid": not reasons,
        "reasons": ",".join(reasons) if reasons else "",
        "entry_price": entry_price,
        "stop_price": stop_price,
        "stop_distance": float(stop_distance),
        "atr14": atr14,
        "risk_dollars": float(risk_dollars),
        "position_size": position_size,
        "exit_trigger": exit_trigger,
        "exit_price": exit_price,
        "exit_date": exit_date,
        "status": "EXIT" if exit_trigger else "OPEN",
    }


def run_executor(
    data: pd.DataFrame,
    signals: pd.DataFrame,
    universe: Iterable[str],
    asof_date: pd.Timestamp | None = None,
    account_equity: float = 100_000.0,
    risk_pct: float = 0.02,
) -> pd.DataFrame:
    """Run executor for signalled symbols using future data for exits."""
    results = []
    symbols = data.columns.get_level_values(0)
    signal_map = dict(zip(signals["symbol"], signals["signal"]))

    if asof_date is None:
        asof_date = data.index.max()

    for symbol in universe:
        if symbol not in symbols:
            continue
        if not signal_map.get(symbol, False):
            continue
        ohlcv = data[symbol].dropna()
        if ohlcv.empty:
            continue
        enriched = add_indicators(ohlcv)
        results.append(
            execute_symbol(
                symbol,
                enriched,
                signal_date=asof_date,
                account_equity=account_equity,
                risk_pct=risk_pct,
            )
        )

    return pd.DataFrame(results)
