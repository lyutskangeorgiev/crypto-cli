# Scope & Validation — Crypto CLI (Requests-Only, Cache-First)

This document locks down **what is in scope** for the current iteration of the Crypto CLI project and provides a **checklist to validate** that the implementation matches the agreed scope.

The goal is to keep the project **focused**, **graded on the right features**, and **aligned with the README/DESIGN**.

---

## 1. Iteration Scope

### 1.1 Core Features

- **CLI**
  - `price` command (current prices; production-ready).
  - `history` command (single-coin OHLCV + analytics: returns, CAGR, max drawdown).
  - Typer-based CLI (`python -m crypto_cli.main`) with `--help` and shell autocompletion.

- **HTTP Layer (Requests-only)**
  - Shared `requests.Session` with:
    - Timeouts
    - Small retry policy on `429` / `5xx`
    - Custom `User-Agent`
  - Error mapping to short, friendly messages (no raw tracebacks).

- **API Key Handling**
  - `CRYPTO_CLI_API_KEY` read from environment in API layer only.
  - Correct CoinGecko header usage:
    - Demo: `x-cg-demo-api-key`
    - Pro:  `x-cg-pro-api-key`
  - API key is **never logged, printed, or included in cache keys/payloads**.

- **Caching**
  - Disk cache under `~/.cache/crypto-cli/` (XDG-friendly).
  - Cache entries: `{fetched_at, status_code, payload}`.
  - Cache key: `METHOD PATH?sorted(query_params)` (no headers, no secrets).
  - TTLs:
    - `price`: ~60 seconds
    - `history`: hours
  - `--no-cache` to bypass cache and force fresh network fetch.

- **Data & Analytics**
  - `price`:
    - Calls `/api/v3/simple/price?ids={ids}&vs_currencies={vs}`.
    - Normalized rows: `{coin, vs, price[, mcap?, volume?]}`.
    - Printed as aligned table (2–4 decimals, consistent columns).
  - `history`:
    - Calls `/coins/{id}/market_chart?vs_currency={vs}&from={unix}&to={unix}`.
    - Validation for `--start/--end` (YYYY-MM-DD, `start <= end`).
    - Normalized DataFrame:
      - `date` (UTC, ascending), `open`, `high`, `low`, `close`, `volume`.
    - `daily_return`: `close_t / close_{t-1} - 1` (first = `NaN`).
    - Analytics:
      - **CAGR**: `(E / S)^(365 / D) - 1`, with guards:
        - `S <= 0` or `D < 1` → return `N/A`.
      - **Max Drawdown**:
        - Running peak; report worst % drawdown and peak→trough dates.
    - Summary block:
      - Period
      - Trading-day count
      - CAGR
      - Max Drawdown (+ dates)
      - Tail table of recent rows

- **UX & Errors**
  - Formatting helpers for:
    - Thousands separators
    - Percentages
    - Aligned tables
  - Command-prefixed errors (e.g. `price: unknown coin`, `history: invalid date`).
  - No unhandled tracebacks in normal usage.

- **Testing**
  - Analytics unit tests:
    - Daily returns: up/down/flat toy series.
    - CAGR: monotonic up/down + guard cases.
    - Max Drawdown: flat, mid-range trough, last-day ATH.
  - CLI “smoke” tests:
    - `price` happy path + invalid coin / invalid vs.
    - `history` invalid date + minimal happy path (fixture-based).
  - HTTP mocks:
    - Retry/backoff on `429` / `5xx`.
    - Cache hit vs `--no-cache` miss.
    - Headers *not* part of cache key.
  - Tests pass locally; unit tests do not depend on live network.

- **Docs & Demo**
  - `README.md`:
    - Describes features in-scope: `price` + staged `history`/analytics.
    - Usage examples and autocompletion setup.
    - API key section: env var, header mapping, no logging/caching.
  - `DESIGN.md`:
    - Module map consistent with actual code layout:
      - `api/fetch_market.py`
      - `api/fetch_history.py`
      - `utils/_session.py`
      - `utils/cache.py`
      - `utils/format.py`, `utils/tables_format.py`
      - `data/transform.py`, `data/analytics.py`
    - Emphasizes requests-only HTTP, caching, analytics.
    - Explicitly excludes web scraping.
  - Demo (2–3 min):
    - `price` → `history` flow.
    - Shows at least one graceful error (e.g. bad coin).
    - API key configured off-camera.
    - Reproducible on a fresh venv.

---

## 2. Explicit Non-Goals (Out of Scope for This Iteration)

These are **not required** to consider the project “done” for this iteration:

- No **SQLite persistence** or `--export csv|json`.
- No extended analytics beyond what’s listed (no volatility, Sharpe, rolling metrics, correlation).
- No REST API (no Flask / FastAPI endpoints, no health/version routes).
- No CI/CD pipelines (no GitHub Actions required for this iteration).
- No full-blown linting/formatting pipelines (e.g., pre-commit, mypy, black) as mandatory scope.
- No web scraping or HTML parsing from exchanges or 3rd-party sites.

Future epics may cover:

- Persistence & Export (SQLite, CSV/JSON export).
- Analytics+ (advanced risk/return metrics, rolling stats, correlation).
- REST API (Flask, health/version endpoints).
- CI & Lint (GitHub Actions, coverage, lint passes).

---

## 3. Scope Validation Checklist

Use this section as a **Go/No-Go checklist** before submission.

### Planning & Foundation

- [ ] `python -m crypto_cli.main --help` works from a **clean venv**.
- [ ] `requirements.txt` installs at least: Typer, requests, pandas, pytest.
- [ ] `.gitignore` excludes: `venv/`, `.venv/`, `/.cache/`, `.env`, `.env.local`, `*.secrets.*`.
- [ ] `.env.example` committed with `CRYPTO_CLI_API_KEY=YOUR_KEY_HERE`.
- [ ] `README.md`:
  - [ ] Describes `price` as the core command.
  - [ ] Mentions staged `history`/analytics as near-term.
  - [ ] Includes examples and autocompletion notes.
- [ ] `DESIGN.md`:
  - [ ] States "requests-only" (no CoinGecko client lib, no scraping).
  - [ ] Describes Typer CLI surface.
  - [ ] Explains API surface + future analytics/cache at a high level.

### CLI Scaffolding (Typer)

- [ ] `price --coins btc,eth --vs usd,eur` appears in `--help` with explanation.
- [ ] `history --coin btc --vs usd --start YYYY-MM-DD --end YYYY-MM-DD` appears in `--help` (at least skeleton).
- [ ] Shell completion instructions in README tested for at least one shell.
- [ ] `--help` for root and subcommands is readable and consistent.

### HTTP Layer & API Key

- [ ] Shared `requests.Session` configured with:
  - [ ] Timeouts.
  - [ ] Retry policy (429/5xx).
  - [ ] Custom `User-Agent`.
- [ ] Friendly, short error messages for network/API errors (no raw stack traces).
- [ ] `CRYPTO_CLI_API_KEY` only read inside API layer.
- [ ] Correct header name used depending on endpoint type (demo vs pro).
- [ ] Logs and cache entries never contain the API key.

### Caching Layer

- [ ] Cache directory: `~/.cache/crypto-cli/` (or XDG-compliant equivalent).
- [ ] Cache entries include `fetched_at`, `status_code`, `payload`.
- [ ] Cache key = `METHOD PATH?sorted(query_params)` (no headers, no secrets).
- [ ] `price` cache TTL ≈ 60 seconds.
- [ ] `history` cache TTL ≈ hours.
- [ ] `--no-cache` flag skips cache and forces a network call.
- [ ] Warm `price` calls are noticeably faster than cold ones.

### Price Command

- [ ] Uses session + cache to call `/api/v3/simple/price`.
- [ ] Defensively parses JSON; missing keys → readable error.
- [ ] Output normalized to rows: `{coin, vs, price[, mcap?, volume?]}`.
- [ ] Table formatting:
  - [ ] 2–4 decimal places.
  - [ ] Consistent columns, aligned.
- [ ] On invalid input (e.g., unknown coin), command exits with **non-zero** status.

### History Command (Data + Analytics)

- [ ] `--start`/`--end` validated:
  - [ ] `YYYY-MM-DD` format.
  - [ ] `start <= end`.
- [ ] Calls `/coins/{id}/market_chart` with correct `vs_currency`, `from`, `to`.
- [ ] Normalized DataFrame:
  - [ ] `date` (UTC, ascending).
  - [ ] `open`, `high`, `low`, `close`, `volume`.
- [ ] `daily_return` computed correctly with first value = `NaN`.
- [ ] Analytics:
  - [ ] CAGR uses `(E/S)^(365/D) - 1` with proper guards.
  - [ ] Max Drawdown computed using running peaks and reports peak→trough dates.
- [ ] Summary block prints:
  - [ ] Period.
  - [ ] Trading-day count.
  - [ ] CAGR (or `N/A`).
  - [ ] Max Drawdown % with dates.
  - [ ] Tail table of recent rows.
- [ ] Edge cases (flat/monotonic prices) behave sensibly.

### UX & Error Handling

- [ ] Formatting helpers for:
  - [ ] Thousands separators.
  - [ ] Percentage formatting.
  - [ ] Aligned tables.
- [ ] Errors are:
  - [ ] Prefixed by command (e.g., `price:` / `history:`).
  - [ ] Short, actionable, and consistent.
- [ ] No raw tracebacks in normal error scenarios.

### Testing & Fixtures

- [ ] Analytics tests:
  - [ ] Daily returns for up/down/flat.
  - [ ] CAGR monotonic + guard cases.
  - [ ] Max Drawdown variants.
- [ ] CLI tests:
  - [ ] `price` happy path.
  - [ ] `price` invalid coin / vs.
  - [ ] `history` invalid date.
  - [ ] `history` minimal happy path (fixture-based).
- [ ] HTTP mocks:
  - [ ] Retry/backoff logic tested via mocked 429/5xx.
  - [ ] Cache hit vs `--no-cache` miss.
  - [ ] Headers do not affect cache key.
- [ ] Tests pass locally; no live network required.

### Documentation & Demo

- [ ] `README.md`:
  - [ ] Features: `price` + staged `history`/analytics only (no overclaim).
  - [ ] Usage examples correct and up to date.
  - [ ] Autocompletion section tested.
  - [ ] API key section clear and consistent with actual behavior.
- [ ] `DESIGN.md`:
  - [ ] Module map matches real files and imports.
  - [ ] Requests-only, no web scraping mentioned.
  - [ ] Caching and analytics properly described.
- [ ] Demo:
  - [ ] Shows `price` + `history` run.
  - [ ] Demonstrates one graceful error.
  - [ ] No secrets visible (API key hidden).
  - [ ] Demo reproducible on fresh venv.

---

## 4. Project-Level Definition of Done

The project is **in scope and done for this iteration** if:

- [ ] `price` and `history` commands run and have helpful `--help`.
- [ ] HTTP uses `requests` only, with timeouts, retries, and custom `User-Agent`.
- [ ] API key is read from env only, never logged, never cached.
- [ ] Cache implemented with correct keys, TTLs, and `--no-cache` bypass.
- [ ] `history` prints normalized series + `daily_return`, CAGR, Max Drawdown (+ dates), and clear summary.
- [ ] Minimum tests pass:
  - [ ] Analytics unit tests.
  - [ ] CLI smoke tests.
  - [ ] HTTP mock tests.
- [ ] `README.md` and `DESIGN.md` match the real implementation.
- [ ] No web scraping is used in this iteration.

If any of the above are **not** satisfied, the feature is **out of scope** for this iteration, and the project is **not yet ready** for final submission.
