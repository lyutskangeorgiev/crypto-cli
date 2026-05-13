# Scope & Validation — Crypto CLI (Requests-Only, Real-Time API)

This document locks down **what is in scope** for the current iteration of the Crypto CLI project and provides a **checklist to validate** that the implementation matches the agreed scope.

The goal is to keep the project **focused**, graded on the finished features, and aligned with the `README.md` and `DESIGN.md`.

---

## 1. Iteration Scope

### 1.1 Core Features

- **CLI**
  - `price` command (current prices; production-ready).
  - Typer-based CLI (`python -m crypto_cli.main`) with global configuration context (`ctx.obj`).
  - Command stubs for `history` and `trending` (logic deferred to next iteration).

- **HTTP Layer (Requests-only)**
  - Shared `requests.Session` utilizing connection pooling.
  - Resilience features using `urllib3.Retry`:
    - Timeouts (Connect/Read).
    - Exponential backoff policy for `429` (Rate Limits) and `5xx` (Server Errors).
    - Custom `User-Agent`.
  - Defensive JSON parsing to catch corrupted payloads or HTML maintenance pages.
  - Error mapping to short, friendly terminal messages (no raw tracebacks).

- **API Key Handling**
  - `COINGECKO_API_KEY` read from environment in the main CLI layer.
  - Correct CoinGecko header usage (`x-cg-demo-api-key`).
  - API key is **never logged or printed** to the terminal.

- **Data Validation & Formatting**
  - **Regex Input Validation**: Coin IDs and vs-currencies are strictly validated against regex patterns and deduplicated.
  - **Query Limits**: Hard limit of maximum 10 coins/currencies per request to protect API bounds.
  - **Dynamic Formatting**: Prices are dynamically formatted (e.g., standard 2-decimals for assets >$1.00; up to 15-point precision for micro-caps <$1.00 with trailing zeros stripped).

- **UX & Errors**
  - User-friendly error categorization (`Category` enum: INPUT, RATE, SERVER, OTHER).
  - Command-prefixed errors.
  - No unhandled tracebacks in normal usage.

- **Docs & Demo**
  - `README.md` accurately describes the `price` command and defers `history`/caching.
  - `DESIGN.md` reflects the accurate file structure and architectural split.
  - Demo shows the `price` flow, error handling (e.g., bad coin), and defensive validation.

---

## 2. Explicit Non-Goals (Out of Scope for This Iteration)

These features are **not required** for the current iteration and are staged for the future roadmap:

- **Caching Layer**: No local disk caching (`~/.cache/`) is implemented in this phase. Every call hits the network.
- **Historical Analytics**: The `history` command logic, OHLCV data fetching, CAGR, and Max Drawdown calculations are deferred.
- **Persistence & Export**: SQLite database storage (`db.py`) and CSV/JSON export are deferred.
- **Trending Command**: The `trending` news/coins command is stubbed but deferred.

---

## 3. Scope Validation Checklist

Use this section as a **Go/No-Go checklist** before submission.

### Planning & Foundation
- [ ] `python -m crypto_cli.main --help` works from a clean venv.
- [ ] `requirements.txt` is accurate.
- [ ] `.gitignore` excludes virtual environments and system files.
- [ ] `README.md` accurately describes the `price` command and mentions `history` as planned.
- [ ] `DESIGN.md` module map matches the actual code layout.

### CLI Scaffolding (Typer)
- [ ] `price` options (`--coins`, `--vs`, `--mcap`, etc.) appear in `--help`.
- [ ] Global configuration (timeouts, api_base) is correctly instantiated via `@app.callback()` and passed via `ctx.obj`.
- [ ] Unfinished commands (`history`, `trending`) exist purely as safe stubs.

### HTTP Layer & Resilience
- [ ] Custom `HTTPAdapter` is mounted explicitly to `"https://api.coingecko.com/"`.
- [ ] Exponential backoff strategy is configured for `429` and `5xx` statuses.
- [ ] Timeouts are explicitly passed to `session.get()`.
- [ ] Defensive parsing catches `JSONDecodeError` and checks the `Content-Type` header.
- [ ] `COINGECKO_API_KEY` is utilized correctly via headers.

### Input Validation
- [ ] `parse_csv_ids` validates input against lowercase alphanumeric/hyphen regex.
- [ ] `parse_csv_vs` validates input against >=2 alphabetical characters regex.
- [ ] Inputs are deduplicated and enforce a maximum length of 10.
- [ ] Invalid input raises a `ValueError` which is caught and printed as a friendly CLI error.

### Data Formatting (`price` command)
- [ ] Returns structured rows for the requested coins and currencies.
- [ ] High-value assets (>= 1.0) format cleanly with thousands separators and 2 decimal points.
- [ ] Low-value assets (< 1.0) format with extended precision, stripping useless trailing zeros.

### Error Handling
- [ ] Bad inputs (e.g. unknown coin) result in clean, handled CLI outputs (no stack traces).
- [ ] Network failures (timeout, connection error) are caught and translated into custom `RuntimeError` messages.
- [ ] Exits with status code `1` on failure to play nicely with shell scripts.

---

## 4. Project-Level Definition of Done

The project is **in scope and done for this iteration** if:

- [ ] The `price` command executes successfully and formats data dynamically.
- [ ] Input strings are sanitized and protected via regex before network execution.
- [ ] HTTP uses `requests.Session` with a fully mounted `urllib3.Retry` adapter.
- [ ] `README.md` and `DESIGN.md` match the implemented code.
- [ ] Error messages are informative and gracefully handled.

If the above are satisfied, the iteration is complete, and remaining architecture (DB, Caching, History) is successfully deferred to the next phase.