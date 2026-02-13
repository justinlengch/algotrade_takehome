from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from trading_system.executer.executer import execute_symbol
from trading_system.screener.indicators import add_indicators
from trading_system.screener.screener import screen_symbol
from trading_system.signaller.signaller import signal_symbol


def _make_ohlcv(
    rows: int = 70,
    start: float = 100,
    end: float = 130,
    high_less_than_close: bool = False,
    volume: float = 1_000_000,
) -> pd.DataFrame:
    close = np.linspace(start, end, rows)
    if high_less_than_close:
        high = close - 1
    else:
        high = close + 1
    low = close - 1

    return pd.DataFrame(
        {
            "Open": close,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": np.full(rows, volume),
        }
    )


def _make_signaller_base() -> pd.DataFrame:
    close = np.concatenate(
        [
            np.linspace(100, 150, 50),
            np.full(19, 140),
            np.array([151]),
        ]
    )
    high = close + 1
    low = close - 1
    volume = np.full(len(close), 1_000_000)
    return pd.DataFrame(
        {
            "Open": close,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": volume,
        }
    )


def test_add_indicators_adds_columns() -> None:
    df = _make_ohlcv()
    enriched = add_indicators(df)
    for column in [
        "sma50",
        "sma10",
        "avgvol50",
        "atr14",
        "pct_change_63",
        "peak_63",
    ]:
        assert column in enriched.columns


def test_screener_price_rule() -> None:
    df = add_indicators(_make_ohlcv(start=2, end=2.5))
    result = screen_symbol("TEST", df)
    assert result["passed"] is False
    assert "price_below_min" in result["reasons"]


def test_screener_volume_rule() -> None:
    df = add_indicators(_make_ohlcv(volume=10_000))
    result = screen_symbol("TEST", df)
    assert result["passed"] is False
    assert "volume_below_min" in result["reasons"]


def test_screener_trend_rule() -> None:
    df = add_indicators(_make_ohlcv(start=130, end=100))
    result = screen_symbol("TEST", df)
    assert result["passed"] is False
    assert "below_sma50" in result["reasons"]


def test_signaller_riser_rule() -> None:
    df = add_indicators(_make_ohlcv(end=120))
    result = signal_symbol("TEST", df)
    assert result["signal"] is False
    assert "riser_below_30pct" in result["reasons"]


def test_signaller_tread_rule() -> None:
    df = add_indicators(_make_signaller_base())
    df.loc[df.index[-5], "Low"] = df.loc[df.index[-5], "Low"] * 0.6
    result = signal_symbol("TEST", df)
    assert result["signal"] is False
    assert "tread_retracement_too_large" in result["reasons"]


def test_signaller_breakout_rule() -> None:
    df = add_indicators(_make_signaller_base())
    result = signal_symbol("TEST", df)
    assert result["signal"] is True


def test_executor_position_sizing() -> None:
    df = add_indicators(_make_ohlcv())
    result = execute_symbol("TEST", df, signal_date=df.index[-1])
    assert result["valid"] is True
    assert result["position_size"] is not None
