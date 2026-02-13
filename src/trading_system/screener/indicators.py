from __future__ import annotations

import pandas as pd


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add screener/signaller indicators to OHLCV data."""
    df = df.copy()
    df["sma50"] = df["Close"].rolling(50).mean()
    df["sma10"] = df["Close"].rolling(10).mean()
    df["avgvol50"] = df["Volume"].rolling(50).mean()

    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr14"] = true_range.rolling(14).mean()

    df["pct_change_63"] = df["Close"].pct_change(63)
    df["peak_63"] = df["High"].rolling(63).max()
    return df
