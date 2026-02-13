from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Iterable

import pandas as pd
import yfinance as yf

CACHE_PATH = Path("data/ohlcv.csv")
UNIVERSE_PATH = Path("data/universe.txt")


def load_universe(path: Path = UNIVERSE_PATH) -> list[str]:
    """Load tickers from the universe file."""
    lines = path.read_text().splitlines()
    return [line.strip() for line in lines if line.strip()]


def _is_cache_fresh(cached: pd.DataFrame) -> bool:
    """Return True if cache contains data through today."""
    if cached.empty:
        return False
    latest = cached.index.max()
    if not isinstance(latest, pd.Timestamp):
        latest = pd.to_datetime(latest)
    return latest.date() >= date.today()


def load_or_fetch_ohlcv(
    universe: Iterable[str], period: str = "1y", interval: str = "1d"
) -> pd.DataFrame:
    """Load cached OHLCV or fetch from Yahoo Finance."""
    if CACHE_PATH.exists():
        cached = pd.read_csv(CACHE_PATH, header=[0, 1], index_col=0, parse_dates=True)
        if _is_cache_fresh(cached):
            return cached

    data = yf.download(
        universe,
        period=period,
        interval=interval,
        group_by="ticker",
        auto_adjust=False,
        threads=False,
    )

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(CACHE_PATH)
    return data
