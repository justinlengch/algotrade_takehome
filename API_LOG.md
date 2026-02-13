# API / Data Log

## 1) Primary Data Source
- **Provider**: Yahoo Finance (via `yfinance`)
- **Why chosen**: Fast to implement, no API key, commonly used for testing/research, good enough for daily OHLCV.
- **Data used**: Daily OHLCV + volume for indicators (SMA(10), SMA(50), ATR(14), 63‑day % change).
- **Date range**: Default 5y to capture enough breakouts for testing.
- **Universe (20 US tech names)**:
  - AAPL, MSFT, GOOGL, AMZN, NVDA
  - META, TSLA, AMD, INTC, ORCL
  - ADBE, CRM, NFLX, QCOM, AVGO
  - CSCO, IBM, TXN, AMAT, MU

## 2) Limitations / Caveats
- **Unofficial API**: `yfinance` is a wrapper around public endpoints; changes can break it.
- **No SLA**: uptime and stability are not guaranteed.
- **Rate limits**: no published limits; intermittent throttling is possible.
- **Data quality**: adjusted vs. raw prices must be handled consistently for returns/indicators.

## 3) Alternatives Considered
- **Alpha Vantage**
  - Pros: official API, stable endpoints, long history.
  - Cons: free tier is very limited (25 requests/day, 5/min).
- **Twelve Data**
  - Pros: generous free tier, clean docs.
  - Cons: credit‑based pricing and per‑request row limits.
