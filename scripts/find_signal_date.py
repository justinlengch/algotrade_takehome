from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from trading_system.screener.market_data import load_or_fetch_ohlcv, load_universe
from trading_system.signaller.signaller import run_signaller


def main() -> None:
    parser = argparse.ArgumentParser(description="Find recent dates with buy signals.")
    parser.add_argument("--period", default="5y", help="Yahoo period (e.g., 5y).")
    parser.add_argument("--interval", default="1d", help="Yahoo interval (e.g., 1d).")
    parser.add_argument("--lookback", type=int, default=120, help="Days to scan back.")
    args = parser.parse_args()

    universe = load_universe()
    data = load_or_fetch_ohlcv(universe, period=args.period, interval=args.interval)
    dates = data.index.unique()

    hits = []
    for day in dates[-args.lookback :]:
        subset = data.loc[:day]
        signals = run_signaller(subset, universe)
        if signals.empty:
            continue
        fired = signals[signals["signal"]]
        if not fired.empty:
            hits.append((day, fired["symbol"].tolist()))

    if not hits:
        print("No signals found in lookback window.")
        return

    for day, symbols in hits:
        print(f"{day.date()}: {', '.join(symbols)}")


if __name__ == "__main__":
    main()
