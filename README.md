# Systematic Momentum Trading

Python implementation of a 3-stage pipeline:
- `Screener`: liquidity + trend filters
- `Signaller`: riser/tread/breakout signal logic
- `Executor`: risk sizing, stop-loss validation, trailing-stop exit

## Requirements

- Python `>= 3.13`
- Dependencies in `pyproject.toml` (`pandas`, `numpy`, `yfinance`, `rich`, `pytest`)

## Setup

```bash
# from repo root
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Data

- Universe file: `data/universe.txt`
- OHLCV cache file: `data/ohlcv.csv`
- Data source: Yahoo Finance via `yfinance`

## Run Pipeline

```bash
python scripts/run_pipeline.py
```

This prints 3 result tables:
- Screener results
- Signaller results
- Executor results (will not show if 0 symbols pass signaller)

## Pipeline Arguments

```bash
python scripts/run_pipeline.py --help
```

- `--period` (default: `1y`)
  - Yahoo period, example: `1y`, `5y`
- `--interval` (default: `1d`)
  - Yahoo interval, example: `1d`
- `--asof` (default: none)
  - Run calculations up to `YYYY-MM-DD`
  - If the date is not a trading day, it snaps to the nearest prior trading day
- `--refresh`
  - Force fresh download (delete local cache first)
- `--html`
  - Export HTML report to `reports/pipeline_results.html`

## Common Commands

```bash
# full run with fresh data
python scripts/run_pipeline.py --period 5y --refresh

# historical replay/backtest style run
python scripts/run_pipeline.py --period 5y --asof 2024-08-01

# export HTML report
python scripts/run_pipeline.py --period 5y --html
```

## Find Historical Signal Dates

Use this helper to find dates in recent history where any symbol fired a buy signal:

```bash
python scripts/find_signal_date.py --period 5y --lookback 180
```

Arguments:
- `--period` (default: `5y`)
- `--interval` (default: `1d`)
- `--lookback` (default: `120`)

## Tests

```bash
pytest -v
```

## Project Structure

```text
src/trading_system/
  screener/
    market_data.py
    indicators.py
    screener.py
  signaller/
    signaller.py
  executer/
    executer.py
scripts/
  run_pipeline.py
  find_signal_date.py
tests/
  test_pipeline.py
```
