# DESIGN.md - Crypto CLI

---

## 1. Overview

- `crypto-cli` is a small command-line tool for fetching cryptocurrency price data.
- The current implementation includes:
  - A Typer-based CLI
  - The `price` command
  - A robust HTTP wrapper (timeouts, retries, user-agent)
  - Clean, readable table formatting
- The design prepares for:
  - A `history` command
  - Daily returns and basic analytics (CAGR, Max Drawdown)
  - Optional tiny disk cache
- Future expansions (not in this milestone) include persistence, export, analytics+, news, and a REST API.

---

## 2. Goals & Non-Goals

### Goals

- Provide a reliable CLI interface with a solid `price` command.
- Maintain a clean architecture separating API, data processing, and utilities.
- Offer clear error messages and helpful `--help` output.
- Ensure testability and maintainability as features grow.
- Prepare internal structure for `history` and analytics.

### Non-Goals (Deferred)

- SQLite storage and file export.
- Advanced analytics like volatility, Sharpe, rolling metrics.
- News or RSS integration.
- Flask API layer.
- Multi-provider API abstraction.

---

## 3. Current Project Structure

- `src/crypto_cli/`
  - `main.py` — CLI entry point (Typer)
  - `db.py` — Placeholder for future DB helpers
  - `api/` — Requests to CoinGecko
    - `fetch_market.py`
    - `fetch_history.py`
  - `data/`
    - `transform.py`
    - `analytics.py` (planned)
  - `utils/`
    - `_session.py`
    - `cache.py` (planned)
    - `db.py`
    - `errors.py`
    - `format.py`
    - `parse.py`
    - `tables_format.py`

---

## 4. Architecture

- **CLI layer (`main.py`)**
  - Defines commands
  - Parses arguments and orchestrates workflow
- **API layer (`api/`)**
  - Handles HTTP communication with CoinGecko
  - Sets query params, headers, timeouts, retries
- **Data layer (`data/`)**
  - Normalizes JSON into rows or frames
  - (Planned) Computes analytics — CAGR, Max Drawdown, daily returns
- **Utils layer (`utils/`)**
  - Shared helpers for formatting, parsing, caching (future)
  - A dedicated `_session.py` for session configuration

---

## 5. CLI Design

### Implemented

- `price --coins BTC,ETH --vs usd`
  - Fetches prices for one or multiple coins
  - Supports multiple vs-currencies
  - Prints aligned, readable output

### Planned

- `history --coin btc --vs usd --start YYYY-MM-DD --end YYYY-MM-DD`
  - Fetch OHLCV data
  - Compute daily returns
  - Add summary and analytics

### UX Notes

- Avoid stack traces for user errors.
- Example usage included in `--help`.
- Provide actionable error messages (“unknown coin”, “invalid date”, etc.).
- Tables should be aligned and numbers formatted consistently.

---

## 6. External API (Requests Layer)

- Provider: **CoinGecko**
- No SDK dependencies; only `requests`
- Endpoints:
  - Spot prices:  
    `/api/v3/simple/price?ids={ids}&vs_currencies={vs}`
  - Historical market data:  
    `/api/v3/coins/{id}/market_chart?vs_currency={vs}&from={unix}&to={unix}`
- HTTP Behavior:
  - Meaningful timeouts
  - Small retry set for 429 and 5xx
  - Custom User-Agent
- JSON parsing is defensive: missing keys → clear error

---

## 7. API Keys

- If CoinGecko enforces keys:
  - Use environment variable: `CRYPTO_CLI_API_KEY`
  - Header names:
    - Public API: `x-cg-demo-api-key`
    - Pro API: `x-cg-pro-api-key`
- Keys should:
  - Never be logged
  - Never be part of cache keys
  - Be kept out of version control

---

## 8. Data Model

### Price Rows

- `coin`: string  
- `vs`: string  
- `price`: float  
- `mcap`: float (optional)  
- `volume`: float (optional)

### History Frame (Planned)

- `date`: UTC datetime  
- `open`: float  
- `high`: float  
- `low`: float  
- `close`: float  
- `volume`: float  
- `daily_return`: float  

---

## 9. Caching Strategy (Planned)

- Small disk cache stored under:
  - `~/.cache/crypto-cli/`
- Cached entries contain:
  - Timestamp
  - Status code
  - JSON payload
- Keys:
  - Built from HTTP method + path + sorted query parameters
  - Never include headers or API keys
- TTL:
  - Price: short (≈ 60 seconds)
  - History: longer (≈ hours)
- `--no-cache` bypasses the cache entirely

---

## 10. Analytics (Planned)

### Daily Return

- Per period:
  
  `daily_return_t = close_t / close_(t-1) - 1`

- First entry has no previous data → set to `NaN`.

### CAGR (Compounded Annual Growth Rate)

- Inputs:
  - `S` = starting close  
  - `E` = ending close  
  - `D` = calendar days  

- Formula:

  `CAGR = (E / S)^(365 / D) - 1`

- Guards:
  - If `S <= 0` or `D < 1` → return `"N/A"`

### Max Drawdown

- Running peak:

  `peak_to_date_t = max(close_0 ... close_t)`

- Drawdown:

  `DD_t = close_t / peak_to_date_t - 1`

- Maximum drawdown:

  `max_drawdown = min(DD_t for all t)`

- Also track:
  - Peak date
  - Trough date

---

## 11. Error Handling

- **Input validation**
  - Reject empty `--coins` / `--vs`
  - (Planned) Validate dates in `YYYY-MM-DD` format and ensure `start <= end`

- **HTTP layer**
  - Timeouts on slow connections
  - Small retry policy on `429` and `5xx` responses
  - Friendly messages like "network error, try again" instead of raw tracebacks

- **API response validation**
  - Check that expected keys exist in the JSON before using them
  - Clear errors when CoinGecko returns unexpected formats

- **Analytics (planned)**
  - If inputs aren’t usable (e.g., only one close value), return `None`
  - Print `"N/A"` instead of crashing or printing bad numbers

---

## 12. Modules & Responsibilities

- **main.py**
  - Defines Typer commands
  - Delegates fetch → transform → format → print
  - Implements `price` (history planned)

- **api/fetch_market.py**
  - Handles spot price requests
  - Assembles parameters
  - Uses `_session.py` for HTTP config

- **api/fetch_history.py** (planned)
  - Fetches historical OHLCV
  - Converts ISO dates to UNIX timestamps

- **data/transform.py**
  - Converts JSON to normalized rows/frames

- **data/analytics.py** (planned)
  - Implements daily returns, CAGR, Max Drawdown

- **utils/_session.py**
  - Builds a session with timeouts, retries, and User-Agent

- **utils/cache.py** (planned)
  - Disk-based TTL caching helpers

- **utils/parse.py**
  - CSV parsing
  - Validates coins, vs-currencies, and (later) dates

- **utils/format.py**
  - Formats numbers, percentages

- **utils/tables_format.py**
  - Produces aligned tables for CLI output

- **db.py / utils/db.py**
  - Reserved for future persistence features

---

## 13. Testing Strategy

### Current

- Smoke tests for `price`
  - Valid input → prints table
  - Invalid coin → readable error + non-zero exit

- Unit tests
  - Parsing helpers (`parse_coins`, `validate_vs`)
  - Table formatting consistency

### Future

- Daily returns tests (up/down/flat)
- CAGR with edge cases
- Max Drawdown (flat, rising, drop)
- HTTP mocking for retries/timeout behavior

---

## 14. Known Limitations

- No `history` command yet
- No analytics
- No caching layer
- No DB persistence
- Only CoinGecko supported
- No REST API
- No export functionality

---

## 15. Future Improvements

- Implement `history` command
- Add daily returns, CAGR, Max Drawdown
- Add disk cache for faster repeated lookups
- Add SQLite persistence + export (`--export csv|json`)
- More analytics: volatility, Sharpe, rolling metrics
- News/RSS data ingestion
- REST API endpoints
- GitHub Actions for automated tests and linting

---

## 16. Glossary

- **Daily Return:** Percent change between two consecutive closes.  
- **CAGR:** Annualized return over a time period.  
- **Max Drawdown:** Worst peak-to-trough decline.  
- **vs_currency:** Quote currency (usd, eur).  
- **OHLCV:** Open, High, Low, Close, Volume.  
