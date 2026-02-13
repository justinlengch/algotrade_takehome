from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
from rich.console import Console
from rich.table import Table

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from trading_system.executer.executer import run_executor
from trading_system.screener.market_data import CACHE_PATH, load_or_fetch_ohlcv, load_universe
from trading_system.screener.screener import run_screener
from trading_system.signaller.signaller import run_signaller


def _build_table(df: pd.DataFrame, title: str, bool_columns: list[str]) -> Table:
    cleaned = df.copy()
    if "reasons" in cleaned.columns and cleaned["reasons"].replace("", pd.NA).isna().all():
        cleaned = cleaned.drop(columns=["reasons"])

    table = Table(title=title, show_lines=False)
    for column in cleaned.columns:
        table.add_column(str(column))

    for _, row in cleaned.iterrows():
        cells = []
        for column in cleaned.columns:
            value = row[column]
            if column in bool_columns and isinstance(value, bool):
                cells.append(
                    f"[green]True[/green]" if value else "[red]False[/red]"
                )
            else:
                cells.append("" if pd.isna(value) else str(value))
        table.add_row(*cells)

    return table


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the trading pipeline.")
    parser.add_argument("--period", default="1y", help="Yahoo period (e.g., 1y, 5y).")
    parser.add_argument("--interval", default="1d", help="Yahoo interval (e.g., 1d).")
    parser.add_argument("--asof", default=None, help="Run using data up to YYYY-MM-DD.")
    parser.add_argument("--refresh", action="store_true", help="Force re-download.")
    parser.add_argument(
        "--html",
        action="store_true",
        help="Export results to reports/pipeline_results.html.",
    )
    args = parser.parse_args()

    if args.refresh and CACHE_PATH.exists():
        CACHE_PATH.unlink()

    universe = load_universe()
    full_data = load_or_fetch_ohlcv(universe, period=args.period, interval=args.interval)

    asof_date = None
    data = full_data
    if args.asof:
        asof_date = pd.to_datetime(args.asof)
        data = full_data.loc[:asof_date]

    console = Console()
    screener_results = run_screener(data, universe)
    if args.html:
        Path("reports").mkdir(parents=True, exist_ok=True)
    if screener_results.empty:
        console.print("\nScreener Results")
        console.print("No screener results (insufficient data for indicators).")
    else:
        screener_results = screener_results.sort_values("passed", ascending=False)
        console.print(
            _build_table(screener_results, "Screener Results", ["passed"])
        )

    signaller_results = run_signaller(data, universe)
    if args.html:
        pass
    if signaller_results.empty:
        console.print("\nSignaller Results")
        console.print("No signaller results (insufficient data for signals).")
    else:
        signaller_results = signaller_results.sort_values("signal", ascending=False)
        console.print(
            _build_table(signaller_results, "Signaller Results", ["signal"])
        )

    executor_results = run_executor(
        full_data, signaller_results, universe, asof_date=asof_date
    )
    if args.html:
        html_sections = [
            "<h2>Screener Results</h2>",
            screener_results.to_html(index=False),
            "<h2>Signaller Results</h2>",
            signaller_results.to_html(index=False),
            "<h2>Executor Results</h2>",
            executor_results.to_html(index=False),
        ]
        Path("reports/pipeline_results.html").write_text("\n".join(html_sections))
    if not executor_results.empty:
        console.print(
            _build_table(executor_results, "Executor Results", ["valid"])
        )


if __name__ == "__main__":
    main()
