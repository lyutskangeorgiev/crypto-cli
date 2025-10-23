# Crypto CLI

A small, reliable command-line tool to fetch cryptocurrency prices and historical data from CoinGecko (requests-only) and compute **CAGR** and **Max Drawdown**. Built for clarity, reproducibility, and a clean demo.

> **Scope (this release):** `price` and `history` commands, tiny disk cache, API key via env var, analytics = CAGR & Max DD.
> **Deferred:** DB persistence, file export, advanced analytics, RSS/news, Flask API.

---

## Features

* **Requests-only** HTTP client (timeouts, small retries, custom UA).
* **Tiny disk cache** to reduce latency and soften rate limits.
* **Two commands**:

  * `price` — spot prices for one or more coins.
  * `history` — historical series + **daily returns**, **CAGR**, **Max Drawdown**.
* **Clean CLI UX**: helpful `--help`, tidy tables, actionable errors.

---

## Requirements

* Python **3.10+**
* Internet connection
* Dependencies: `typer`, `requests`, `pandas`, `pytest` (for tests)

---

## Install

```bash
# clone your repo
git clone https://github.com/<you>/<repo>.git
cd <repo>

# create & activate venv
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

# install deps
pip install -r requirements.txt
```

---

## API Key & Security

CoinGecko now expects a key for many public/pro endpoints.

* **Set your key in an environment variable** (never hardcode):

  * Env var name: **`CRYPTO_CLI_API_KEY`**
* **Header usage** (handled inside the `api/` layer):

  * Public/demo base `api.coingecko.com` → header **`x-cg-demo-api-key`**
  * Pro base `pro-api.coingecko.com` → header **`x-cg-pro-api-key`**
* **Do not** pass keys via CLI flags or query params.
* Keys are **never logged or cached**; headers are excluded from cache keys.

Optional helper files:

```
# .gitignore (add)
.env
.env.local
*.secrets.*

# .env.example (commit with placeholders only)
CRYPTO_CLI_API_KEY=YOUR_KEY_HERE
```

Set the key before running:

```bash
# macOS/Linux
export CRYPTO_CLI_API_KEY="your_real_key_here"

# Windows PowerShell
$env:CRYPTO_CLI_API_KEY = "your_real_key_here"
```

---

## Quickstart

```bash
# See help
python -m crypto_cli.main --help

# Get spot prices
python -m crypto_cli.main price --coins btc,eth --vs usd

# Get history + analytics (CAGR, Max DD)
python -m crypto_cli.main history --coin btc --vs usd --start 2023-01-01 --end 2023-12-31
```

---

## Commands

### `price`

Fetch spot prices for one or more coins in a given vs-currency.

**Usage**

```bash
python -m crypto_cli.main price --coins <csv_ids> --vs <currency> [--no-cache]
```

**Examples**

```bash
python -m crypto_cli.main price --coins btc,eth --vs usd
python -m crypto_cli.main price --coins sol --vs eur --no-cache
```

**Notes**

* `--coins` uses official CoinGecko IDs (check their docs/UI for exact IDs).
* `--no-cache` forces a fresh network call.

---

### `history`

Fetch a historical series and print daily returns + a summary with **CAGR** and **Max Drawdown**.

**Usage**

```bash
python -m crypto_cli.main history \
  --coin <id> --vs <currency> \
  --start YYYY-MM-DD --end YYYY-MM-DD \
  [--no-cache]
```

**Example**

```bash
python -m crypto_cli.main history --coin btc --vs usd --start 2023-01-01 --end 2023-12-31
```

**Output**

* **Summary**: period, trading-day count, **CAGR**, **Max Drawdown** (percentage and peak→trough dates)
* **Tail table**: last rows with `date`, `close`, `daily_return`

---

## Analytics Definitions

* **Daily Return**
  ( r_t = \frac{\text{close}*t}{\text{close}*{t-1}} - 1 )
  First value is NA (no prior day) and is not used in aggregates.

* **CAGR (Compounded Annual Growth Rate)**
  Using first close (S), last close (E), and calendar days (D):
  ( \text{CAGR} = \left(\frac{E}{S}\right)^{\frac{365}{D}} - 1 )
  Guards: if (S \le 0) or (D < 1), report **N/A**.

* **Max Drawdown (percentage + dates)**
  Track a running peak of `close`.
  ( \text{DD}_t = \frac{\text{close}_t}{\text{peak_to_date}} - 1 \le 0 )
  Max DD is the minimum DD over the period; report value and **peak→trough** dates.
  Edge cases: monotonic rise → Max DD = 0.00%; flat series → CAGR = 0.00%, Max DD = 0.00%.

---

## Caching

* Location: `~/.cache/crypto-cli/`
* Cache key: `METHOD PATH?sorted(query_params)` (headers **not** included)
* Format: JSON `{ fetched_at, status_code, payload }`
* Default TTLs:

  * `price`: ~60 seconds
  * `history`: ~6 hours
* Bypass cache with `--no-cache`.

---

## Project Layout

```
src/crypto_cli/
  main.py                 # Typer commands: price, history
  api/
    __init__.py
    fetch_market.py       # requests+cache for spot price (adds API key header if set)
    fetch_history.py      # requests+cache for historical data (adds API key header if set)
  data/
    __init__.py
    transform.py          # JSON → DataFrame normalization; UTC parsing; dtype enforcement
    analytics.py          # daily returns, CAGR, Max Drawdown (pure)
  utils/
    __init__.py
    cache.py              # disk cache: keying, TTL, get/put
    parse.py              # input validation (coins/vs/dates)
    format.py             # table/number/percent formatting; concise errors
    db.py                 # present but NOT used in this release
tests/
  ...                     # analytics unit tests + CLI smokes
```

---

## Troubleshooting

* **Unauthorized / key required**
  Ensure `CRYPTO_CLI_API_KEY` is set. Confirm base URL → header mapping (demo vs pro handled inside `api/*`).

* **Too many requests / 429**
  Let the cache do its job. Avoid rapid polling. Respect TTLs.

* **Invalid coin id / vs**
  Use official CoinGecko IDs and valid vs currencies (e.g., `usd`, `eur`). Check spelling/case.

* **Bad date format**
  Use `YYYY-MM-DD` and ensure `start <= end`.

* **Empty output**
  The date range may lack data; widen the range or choose another coin.

---

## Roadmap

* **Persistence & Export:** SQLite upserts for OHLCV + returns; `--export csv|json`.
* **Analytics+:** Annualized volatility, Sharpe (configurable RF), rolling metrics, correlation, SMA regimes.
* **Trending (stable):** RSS ingestion (dedupe by URL hash).
* **REST API:** Flask parity endpoints.
* **HTTP enhancements:** honor `Retry-After`, circuit breaker, configurable base URL.
* **CI & Quality:** GitHub Actions, `ruff`/`flake8`, pre-commit hooks.

