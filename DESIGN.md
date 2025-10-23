# DESIGN.md — Crypto CLI

> **Scope (this release):** CLI with `price` and `history`, requests-only HTTP, tiny disk cache, and two analytics (**CAGR** & **Max Drawdown**).
> **Deferred:** DB persistence, file export, advanced analytics, RSS/news, Flask API.

---

## 1. Overview

A small, reliable CLI that fetches cryptocurrency spot and historical data from CoinGecko (requests-only) and computes:

* **CAGR** (Compounded Annual Growth Rate)
* **Max Drawdown** (percentage and peak→trough dates)

Priorities: clarity, reproducibility, testability, and minimal moving parts.

---

## 2. Goals & Non-Goals

### Goals

* Two solid commands: `price`, `history`
* Robust HTTP wrapper (timeouts, small retries, backoff, custom User-Agent)
* Tiny disk cache to soften rate limits and speed up UX
* Pure analytics in a dedicated module
* Helpful `--help` and tidy, readable tables

### Non-Goals (deferred)

* SQLite storage and `--export`
* Volatility/Sharpe/rolling metrics/correlation/regimes
* News/RSS scraping
* Flask REST API

---

## 3. Current Project Structure

```
src/
└─ crypto_cli/
   ├─ api/
   │  ├─ __init__.py
   │  ├─ fetch_history.py
   │  └─ fetch_market.py
   ├─ data/
   │  ├─ __init__.py
   │  ├─ analytics.py
   │  └─ transform.py
   ├─ utils/
   │  ├─ __init__.py
   │  ├─ cache.py
   │  ├─ format.py
   │  ├─ parse.py
   │  └─ db.py        # present but NOT used in this release
   └─ main.py
```

> Note: `utils/db.py` exists but is **not used** in this sprint (persistence is deferred).

---

## 4. Architecture

```
Typer CLI (main.py)
   ├── price command
   └── history command
        │
        ▼
API Layer (requests + tiny cache)
   ├── api/fetch_market.py   # spot price calls
   └── api/fetch_history.py  # historical calls
        │
        ▼
Transform & Analytics
   ├── data/transform.py     # JSON → DataFrame/rows
   └── data/analytics.py     # daily returns, CAGR, Max DD (pure)
        │
        ▼
Utilities
   ├── utils/parse.py        # input validation (coins/vs/dates)
   ├── utils/cache.py        # disk cache (TTL, stable keys)
   └── utils/format.py       # tables & number/percent formatting
```

---

## 5. CLI Design

### Commands

* `price --coins btc,eth --vs usd [--no-cache]`
  Fetch spot prices for one or more coin IDs in a vs-currency.

* `history --coin btc --vs usd --start 2023-01-01 --end 2023-12-31 [--no-cache]`
  Fetch historical series, compute `daily_return`, **CAGR**, **Max Drawdown**, and print a summary plus a small tail table.

### UX Notes

* Aligned tables; thousands separators; percentages with 2–4 decimals
* Clear, actionable errors (unknown coin/vs, invalid dates)
* `--help` shows one runnable example per command

---

## 6. External API (requests-only)

**Provider:** CoinGecko
**Client:** custom `requests.Session` inside `api/*`.

**Endpoints**

* `/api/v3/simple/price?ids={ids}&vs_currencies={vs}` (spot)
* `/api/v3/coins/{id}/market_chart?vs_currency={vs}&from={unix}&to={unix}` (history)

**HTTP Policy**

* Timeouts: connect = 3s, read = 10s (configurable)
* Retries: 2–3 on idempotent GETs for 429/5xx with exponential backoff (0.5s → 1.0s → 2.0s)
* Headers: `User-Agent` from config; `Accept: application/json`
* Caching: disk cache wraps responses; `--no-cache` forces fresh call
* Errors: mapped to short CLI messages; no stack traces in normal runs

---

## 7. API Keys (Demo/Pro)

* CoinGecko now expects a key for many public/pro endpoints.
* **Environment variable:** `CRYPTO_CLI_API_KEY` (never hardcode, never pass via CLI flags).
* **Header names (set inside `api/*` only):**

  * Public/demo base `api.coingecko.com` → `x-cg-demo-api-key`
  * Pro base `pro-api.coingecko.com` → `x-cg-pro-api-key`
* Keys are **never logged** or cached; headers are excluded from cache keys.

Optional repo hygiene:

```
# .gitignore
.env
.env.local
*.secrets.*

# .env.example (commit placeholders only)
CRYPTO_CLI_API_KEY=YOUR_KEY_HERE
```

---

## 8. Data Model (in-memory only)

**Price rows (display)**

| column | type  | example  |
| -----: | :---- | :------- |
|   coin | str   | btc      |
|     vs | str   | usd      |
|  price | float | 62754.12 |
|  mcap? | float | optional |

**History frame (normalized)**

| column          | type           | notes                         |
| --------------- | -------------- | ----------------------------- |
| date            | datetime (UTC) | ascending, unique per point   |
| open, high, low | float          | from API                      |
| close           | float          | used for returns/analytics    |
| volume          | float          | optional                      |
| daily_return    | float          | pct change of close; first NA |

---

## 9. Caching Strategy

* Location: `~/.cache/crypto-cli/` (XDG compatible path OK)
* Key: `METHOD PATH?sorted(query_params)` (stable parameter ordering; **no headers**)
* Format: JSON `{ "fetched_at": <iso>, "status_code": <int>, "payload": <object> }`
* TTLs (defaults): `price` ≈ 60s, `history` ≈ 6h
* Bypass cache with `--no-cache`

---

## 10. Analytics (definitions & guards)

**Daily Return**
`r_t = close_t / close_{t-1} − 1`
First observation is NA and excluded from aggregates.

**CAGR (Compounded Annual Growth Rate)**
Using first close `S`, last close `E`, and calendar days `D`:
`CAGR = (E / S)^(365 / D) − 1`
Guards: if `S ≤ 0` or `D < 1`, return **N/A**.

**Max Drawdown (percentage + dates)**
Track a running peak of `close`.
`DD_t = close_t / peak_to_date − 1` (≤ 0)
Max DD is the minimum `DD_t`; report value and **peak_date → trough_date**.

Edge cases: monotonic rise → Max DD = 0.00%; flat series → CAGR = 0.00%, Max DD = 0.00%.

---

## 11. Error Handling

* Inputs: non-empty coins/vs; dates in `YYYY-MM-DD`; `start ≤ end`
* HTTP: timeouts, retries/backoff; friendly “try again” hints; respect `--no-cache`
* API shape: defensive JSON access; clear messages on missing fields
* Analytics: render “N/A” when insufficient data or invalid inputs

---

## 12. Modules & Responsibilities

* `main.py` — Typer commands. Orchestrates parse → fetch → transform → analytics → print.
* `api/fetch_market.py` — Spot price HTTP (requests+cache), parameter prep, JSON return.
* `api/fetch_history.py` — Historical HTTP (requests+cache), date→unix conversion, JSON return.
* `data/transform.py` — JSON → normalized rows/frames; UTC parsing; dtype enforcement.
* `data/analytics.py` — Pure functions: daily returns, CAGR, Max Drawdown.
* `utils/parse.py` — Input validation/parsing (coins/vs/dates), small helpers.
* `utils/cache.py` — Disk cache get/put, TTL check, stable keying.
* `utils/format.py` — Table/number/percent formatting; concise error helpers.
* `utils/db.py` — Present but unused in this release (future persistence).

---

## 13. Planned Interfaces (signatures only)

> These define **what** each function does, not how. Keep analytics pure (no I/O).

**`main.py`**

* `price(coins: str, vs: str, no_cache: bool = False) -> None`
* `history(coin: str, vs: str, start: str, end: str, no_cache: bool = False) -> None`

**`api/fetch_market.py`**

* `get_simple_price(ids: list[str], vs: str, *, no_cache: bool = False) -> dict`

**`api/fetch_history.py`**

* `get_market_chart_range(coin_id: str, vs: str, start_date: "date", end_date: "date", *, no_cache: bool = False) -> dict`

**`data/transform.py`**

* `to_price_rows(payload: dict, vs: str) -> list[dict]`
* `to_history_frame(payload: dict) -> "pd.DataFrame"`

**`data/analytics.py`**

* `compute_daily_returns(df) -> "pd.DataFrame"`
* `cagr(df) -> float | None`
* `max_drawdown(df) -> tuple[float, "datetime | None", "datetime | None"]`

**`utils/parse.py`**

* `parse_date(iso: str) -> "date"`
* `parse_coins(csv: str) -> list[str]`
* `validate_vs(vs: str) -> str`

**`utils/cache.py`**

* `get(key: str, ttl_s: int) -> dict | None`
* `set(key: str, payload: dict) -> None`
* `make_key(path: str, params: dict) -> str`

**`utils/format.py`**

* `table(rows: list[dict], columns: list[str]) -> str`
* `pct(x: float | None) -> str`
* `num(x: float | None, decimals: int = 2) -> str`
* `err(msg: str, *, where: str) -> str`

---

## 14. Testing Strategy

**Unit (priority)**

* Daily returns: short up/down/flat sequences
* CAGR: monotonic up/down with explicit dates (guard `S ≤ 0`, `D < 1`)
* Max Drawdown: flat; classic peak→trough; last-day ATH

**CLI smokes**

* `price` happy path + invalid coin
* `history` invalid dates + minimal happy path (fixture or mocked HTTP)

**HTTP wrapper**

* Mock `requests.Session.get` in `api/*`:

  * correct params/headers
  * retry/backoff on 429/5xx
  * timeout behavior
  * cache hit vs `--no-cache` miss

**Fixtures**

* Tiny JSON snapshots for price/history to avoid flaky network in tests

---

## 16. Known Limitations

* No persistence/export/API
* Single-asset analytics; only CAGR & Max DD
* SDK conveniences absent—manual param math/pagination if needed

---

## 17. Future Improvements

**Persistence & Export**

* SQLite upserts for OHLCV + returns; `--store`
* `--export csv|json`

**Analytics+**

* Annualized volatility; Sharpe (configurable RF)
* Rolling 30-day volatility; rolling Max Drawdown
* Multi-asset correlation matrix; SMA(20/60) regime flags

**ETrending (Stable)**

* RSS ingestion (avoid brittle scraping), URL-hash dedupe, minimal fields

**REST API**

* Flask endpoints mirroring CLI; health/version; curl docs

**HTTP Client Enhancements**

* Honor `Retry-After` on 429; circuit breaker after N failures
* Pluggable base URL (mirror/alt APIs)

**ECI & Quality**

* GitHub Actions pipeline; `ruff`/`flake8`; pre-commit hooks

---

## 18. Risks & Mitigations

* API changes / rate limits → caching, retries/backoff, friendly errors
* Time pressure → ultra-lean scope; implement analytics before polish
* Floating-point noise → fixed display precision; tolerance-based assertions in tests

---

## 19. Glossary

* **CAGR:** annualized growth from first to last value across calendar days
* **Max Drawdown:** worst peak-to-trough loss (percentage) within the range
* **vs_currency:** quote currency for price (e.g., `usd`)
