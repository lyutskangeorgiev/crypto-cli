# 🚀 crypto-cli
_A small, Typer-based CLI for crypto price data_

---

## Overview

`crypto-cli` is a lightweight command-line tool for querying real-time cryptocurrency prices.

It focuses on:

- A clear, discoverable CLI (Typer)
- Safe HTTP handling (timeouts, retries, friendly errors)
- Readable, table-style output

At the moment, the tool provides a **single core command**: `price`.

---

## Features (current)

### ✅ CLI & project foundation
- Typer-based command structure  
- Helpful `--help` output with usage and options  
- Clean package layout (`crypto_cli` as a module)  
- Works from a clean virtual environment with `requirements.txt`  

### ✅ `price` command
- Multiple coins via `--coins` (e.g. `btc,eth,sol`)  
- Multiple vs-currencies via `--vs` (e.g. `usd,eur`)  
- Validation of input symbols  
- Non-zero exit codes and readable error messages on invalid input / HTTP issues  

### ✅ HTTP client
- Configured timeout  
- Small retry policy  
- Custom User-Agent header  
- No raw stack traces shown to the user  

### ✅ Output formatting
- Aligned table-like output  
- Consistent decimal formatting (2–4 decimals)  
- Market cap / 24h volume columns when available from the API  

---

## Installation

```bash
git clone <your-repo-url>
cd crypto-cli

python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate

pip install -r requirements.txt
```
---

## Autocompletion

### Enable autocompletion for the current session:

```bash
eval "$(python -m crypto_cli.main --show-completion)"
```

### Install autocompletion permanently:

```bash
python -m crypto_cli.main --install-completion
```

Restart your shell afterward
---

## Usage

### Fetch the price of one or more cryptocurrencies:

```bash
python -m crypto_cli.main price --coins btc --vs usd
```

### Multiple coins:

```bash
python -m crypto_cli.main price --coins btc,eth,sol --vs usd
```

### Multiple vs-currencies:

```bash
python -m crypto_cli.main price --coins btc --vs usd,eur
```

---

## Current Features

- **Typer CLI** with helpful `--help` output  
- **price** command with multi-coin and multi-vs support  
- Input validation and human-friendly error messages  
- Timeout + retry HTTP configuration  
- Custom User-Agent header  
- Table-style output with:
  - aligned columns  
  - fixed decimals  
  - market cap and volume when available  

---

## Future Features (planned)

These features are planned for upcoming versions:

### Historical data
-Fetch OHLCV data for a selected date range and print a normalized table.

### Daily return calculations
-Compute day-to-day percentage changes for closing prices.

### Analytics
-Add statistical measures such as CAGR and maximum drawdown.

### Summary blocks
-Show a concise overview for historical data (period, trading days, metrics).

### SQLite storage
-Store fetched prices and historical data locally.

### Flask REST API
-Optional API layer to expose price and history endpoints.

### Testing suite
-Basic CLI and analytics tests to ensure correctness.

