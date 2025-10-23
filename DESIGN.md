# DESIGN.md — Crypto CLI

> **Scope (this release):** CLI with `price` and `history`, requests-only HTTP, tiny disk cache, and two analytics (**CAGR** & **Max Drawdown**).
> **Deferred:** DB persistence/exports, advanced analytics, news/RSS, Flask API.

---

## Table of Contents

1. [Overview](#overview)
2. [Goals & Non-Goals](#goals--non-goals)
3. [Current Project Structure](#current-project-structure)
4. [Architecture](#architecture)
5. [CLI Design](#cli-design)
6. [External API (requests-only)](#external-api-requests-only)
7. [Data Model (in-memory)](#data-model-in-memory)
8. [Caching Strategy](#caching-strategy)
9. [Analytics (definitions & guards)](#analytics-definitions--guards)
10. [Error Handling](#error-handling)
11. [Modules & Responsibilities](#modules--responsibilities)
12. [Planned Interfaces (per file)](#planned-interfaces-per-file)
13. [Testing Strategy](#testing-strategy)
14. [Release Plan (≤10 days)](#release-plan-10-days)
15. [Known Limitations](#known-limitations)
16. [Future Improvements (Epics Backlog)](#future-improvements-epics-backlog)
17. [Risks & Mitigations](#risks--mitigations)
18. [Glossary](#glossary)

---

## Overview

A small, reliable CLI that fetches cryptocurrency spot and historical data from CoinGecko **using only `requests`**, computes:

* **CAGR** (Compounded Annual Growth Rate)
* **Max Drawdown** (percentage and peak→trough dates)

and prints concise, readable summaries. Design emphasizes clear seams, testability, and minimal moving parts.

---

## Goals & Non-Goals

### Goals

* Two solid commands: `price`, `history`.
* Robust HTTP (timeouts, retries, UA) behind a tiny wrapper.
* Disk cache for resilience/rate limits.
* Pure analytics in a dedicated module.
* Helpful `--help` and tidy tables.

### Non-Goals (deferred)

* SQLite storage and `--export`.
* Volatility/Sharpe/rolling/correlations/regimes.
* News/RSS scraping.
* Flask REST API.

---

## Current Project Structure

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
   │  └─ db.py           # present but NOT used in this release
   └─ main.py

---

## Architecture

```
         ┌─────────────────┐
         │    Typer CLI    │  main.py
         └───────┬─────────┘
                 │ user opts / formatted output
┌────────────────┴───────────────────────────────────────┐
│                   Command layer                         │
│  price, history → orchestrate fetch → transform → stats │
└───────────────┬─────────────────────────────────────────┘
                │ normalized data / frames
                ▼
┌─────────────────────────────────────────────────────────┐
│                   Domain / Utilities                    │
│  api/fetch_market.py  (spot price via requests+cache)   │
│  api/fetch_history.py (historical via requests+cache)   │
│  data/transform.py    (JSON → DataFrame normalization)  │
│  data/analytics.py    (daily returns, CAGR, Max DD)     │
│  utils/parse.py       (validate coins/vs/dates)         │
│  utils/cache.py       (disk cache, TTL, stable keys)    │
│  utils/format.py      (tables, number/percent formats)  │
└─────────────────────────────────────────────────────────┘
                │
                ▼
             CoinGecko API
```

---

## CLI Design

### Commands

* `price --coins btc,eth --vs usd [--no-cache]`
  Fetch spot prices for one or more coin IDs in a vs-currency.
* `history --coin btc --vs usd --start 2022-01-01 --end 2023-12-31`
  Fetch historical series, compute `daily_return`, **CAGR**, **Max Drawdown**, and print a summary + tail table.

### UX

* Aligned tables; thousands separators; percentages with 2–4 decimals.
* Clear, actionable errors (unknown coin/vs, invalid date range).
* `--help` shows one runnable example per command.

---

## External API (requests-only)

**Provider:** CoinGecko (public, no key)
**Client:** custom `requests.Session` inside the `api/*` modules.

**Endpoints used:**

* `/api/v3/simple/price?ids={ids}&vs_currencies={vs}` (spot)
* `/api/v3/coins/{id}/market_chart?vs_currency={vs}&from={unix}&to={unix}` (history)
  *Prefer `market_chart` for robust close series; call `ohlc` only if later required.*

**HTTP Policy**

* **Timeouts:** connect=3s, read=10s (configurable).
* **Retries:** 2–3 on idempotent GETs for 429/5xx with exponential backoff (0.5s → 1s → 2s).
* **Headers:** `User-Agent` from config; `Accept: application/json`.
* **Caching:** disk cache wraps HTTP; `--no-cache` forces a fresh call.
* **Errors:** mapped to short CLI messages; no stack traces in normal runs.

* **API Keys (this build): The CLI reads an optional key from the environment variable CRYPTO_CLI_API_KEY. Keys are injected only in the api/ layer as an HTTP header (e.g., Authorization: Bearer <token>), are never logged or printed, and are excluded from cache keys. We do not accept keys via CLI flags or query parameters. For local dev, contributors may copy .env.example to .env.local (ignored by git) and set values there or in their shell profile.
---

## Data Model (in-memory)

### Price rows (display only)

| column | type  | example    |
| :----: | :---- | :--------- |
|  coin  | str   | `btc`      |
|   vs   | str   | `usd`      |
|  price | float | `62754.12` |
|  mcap? | float | optional   |

### History frame (normalized)

| column          | type           | notes                         |
| --------------- | -------------- | ----------------------------- |
| date            | datetime (UTC) | ascending, unique per point   |
| open, high, low | float          | from API                      |
| close           | float          | used for returns/analytics    |
| volume          | float          | optional                      |
| daily_return    | float          | pct change of close; first NA |

---

## Caching Strategy

* **Location:** `~/.cache/crypto-cli/` (XDG-compatible OK)
* **Key:** `METHOD PATH?sorted(query_params)` (stable parameter ordering)
* **Format:** JSON `{ fetched_at, status_code, payload }`
* **TTL:** `price` ≈ 60s; `history` ≈ 6h
* **Bypass:** `--no-cache`

---

## Analytics (definitions & guards)

### Daily Return

`r_t = close_t / close_{t-1} − 1` (first NA; exclude from aggregates).

### CAGR

Inputs: first close `S`, last close `E`, calendar days `D`.
If `S ≤ 0` or `D < 1` → **N/A**.
`CAGR = (E / S)^(365 / D) − 1`.

### Max Drawdown

Track running peak of `close`.
`DD_t = close_t / peak_to_date − 1` (≤ 0).
**Max DD** = minimum `DD_t`; report percentage and **peak_date → trough_date**.

Edge cases: monotonic rise → Max DD = 0.00%; flat series → CAGR = 0.00%, Max DD = 0.00%.

---

## Error Handling

* **Inputs:** non-empty coins/vs; `YYYY-MM-DD` dates; `start ≤ end`.
* **HTTP:** timeouts, retries/backoff; friendly “try again” hints; respect `--no-cache`.
* **API shape:** defensive JSON access; clear messages on missing fields.
* **Analytics:** render “N/A” when insufficient data or invalid inputs.

---

## Modules & Responsibilities

* **`main.py`** — Typer commands. Orchestrates parse → fetch → transform → analytics → print.
* **`api/fetch_market.py`** — Spot price HTTP (requests+cache), parameter prep, JSON return.
* **`api/fetch_history.py`** — Historical HTTP (requests+cache), date → unix conversion, JSON return.
* **`data/transform.py`** — JSON → normalized rows/frames; UTC parsing; dtype enforcement.
* **`data/analytics.py`** — Pure functions: daily returns, CAGR, Max Drawdown.
* **`utils/parse.py`** — Input validation/parsing (coins/vs/dates), small helpers.
* **`utils/cache.py`** — Disk cache get/put, TTL check, stable keying.
* **`utils/format.py`** — Table/number/percent formatting; concise error helpers.
* **`utils/db.py`** — *Present but unused in this release (future persistence).*

---

## Planned Interfaces (per file)

> Signatures show **what** each piece should do (no implementations here).

### `main.py`

* `price(coins: str, vs: str, no_cache: bool=False) -> None`
* `history(coin: str, vs: str, start: str, end: str, no_cache: bool=False) -> None`

### `api/fetch_market.py`

* `get_simple_price(ids: list[str], vs: str, *, no_cache: bool=False) -> dict`

  * Performs GET `/simple/price`, applies timeouts/retries/UA, integrates disk cache.

### `api/fetch_history.py`

* `get_market_chart_range(coin_id: str, vs: str, start_date: datetime.date, end_date: datetime.date, *, no_cache: bool=False) -> dict`

  * Performs GET `/coins/{id}/market_chart?vs_currency=&from=&to=`, handles unix seconds.

### `data/transform.py`

* `to_price_rows(payload: dict, vs: str) -> list[dict]`
* `to_history_frame(payload: dict) -> "pd.DataFrame"`  *(date, o/h/l/c, volume; UTC, ascending)*

### `data/analytics.py`

* `compute_daily_returns(df) -> "pd.DataFrame"`  *(adds `daily_return`; drops first NA)*
* `cagr(df) -> float | None`
* `max_drawdown(df) -> tuple[float, "datetime|None", "datetime|None"]`

### `utils/parse.py`

* `parse_date(iso: str) -> "datetime.date"`  *(validates YYYY-MM-DD)*
* `parse_coins(csv: str) -> list[str]`
* `validate_vs(vs: str) -> str`

### `utils/cache.py`

* `get(key: str, ttl_s: int) -> dict | None`
* `set(key: str, payload: dict) -> None`
* `make_key(path: str, params: dict) -> str`  *(stable ordering)*

### `utils/format.py`

* `table(rows: list[dict], columns: list[str]) -> str`
* `pct(x: float | None) -> str`
* `num(x: float | None, decimals: int=2) -> str`
* `err(msg: str, *, where: str) -> str`

---

## Testing Strategy

**Unit (priority)**

* Daily returns: short up/down/flat sequences.
* CAGR: monotonic up/down with explicit dates (guard for `S<=0`, `D<1`).
* Max Drawdown: flat; classic peak→trough; last-day ATH.

**CLI smokes**

* `price` happy path + invalid coin.
* `history` invalid dates + minimal happy path (fixture or mocked HTTP).

**HTTP**

* Mock `requests.Session.get` in `api/*`:

  * correct params/headers
  * retry/backoff on 429/5xx
  * timeout behavior
  * cache hit vs `--no-cache` miss

**Fixtures**

* Tiny JSON snapshots for price/history to avoid flaky network in tests.

---

## Known Limitations

* No persistence/export/API.
* Single-asset analytics; only CAGR & Max DD.
* SDK conveniences absent—manual param math/pagination if needed.

---

## Future Improvements

**Persistence & Export**

* SQLite upserts for OHLCV + derived returns; `--store`
* `--export csv|json`

**EAnalytics+**

* Annualized volatility; Sharpe (configurable RF)
* Rolling 30-day volatility; rolling Max DD
* Multi-asset correlation matrix; SMA(20/60) regime flags

**Trending (Stable)**

* RSS ingestion (avoid brittle scraping), URL-hash dedupe, minimal fields

**REST API**

* Flask endpoints mirroring CLI; health/version; curl docs

**HTTP Client Enhancements**

* Respect `Retry-After` on 429; circuit breaker after N failures
* Pluggable base URL (mirror/alt APIs)

**EQuality & CI**

* GitHub Actions pipeline; `ruff`/`flake8`; pre-commit hooks

---

## Risks & Mitigations

* **API changes / rate limits:** caching, retries/backoff, friendly errors.
* **Time pressure:** ultra-lean scope; implement analytics before polish.
* **Floating-point noise:** fixed display precision; tolerance-based assertions in tests.

---

## Glossary

* **CAGR:** annualized growth from first to last value across calendar days.
* **Max Drawdown:** worst peak-to-trough loss (percentage) within the range.
* **vs_currency:** quote currency for price (e.g., `usd`).
