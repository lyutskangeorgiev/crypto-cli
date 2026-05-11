# crypto-cli
_A small, Typer-based CLI for crypto price data_

---

## Overview

`crypto-cli` is a lightweight command-line tool for querying real-time cryptocurrency prices.

It focuses on:

- A clear, discoverable CLI (Typer)
- Safe HTTP handling (timeouts, retries, friendly errors)
- Readable, table-style output

At the moment, the tool provides a **single core command**: `price`. 
*(Note: A `history` command featuring daily returns and analytics is currently planned and staged for the next iteration).*

---

## Features

### CLI & Project Foundation
- Typer-based command structure.
- Helpful `--help` output with usage and options.
- Clean package layout (`crypto_cli` as a module).
- Works from a clean virtual environment with `requirements.txt`.

### `price` Command
- Fetch prices for one or multiple coins via `--coins` (e.g., `bitcoin,ethereum,solana`).
- Support for multiple vs-currencies via `--vs` (e.g., `usd,eur`).
- Optional data columns: add Market Cap (`--mcap`), 24h Volume (`--vol`), 24h Change (`--change`), and Last Updated Timestamp (`--updated`).
- Strict validation of input symbols.
- Non-zero exit codes and readable error messages on invalid input / HTTP issues.

### HTTP Client
- Configured connection and read timeouts.
- Small retry policy for `429` (Rate Limit) and `5xx` (Server) errors.
- Custom `User-Agent` header.
- Friendly error handling (no raw stack traces shown to the user).

### Planned Features (Near-Term)
- **`history` Command**: Fetch historical OHLCV data.
- **Analytics**: Calculate Compounded Annual Growth Rate (CAGR) and Max Drawdown.
- **Caching**: Local disk caching for faster repeated lookups.

---

## Configuration & API Key

This tool interacts with the CoinGecko API. To authenticate and avoid severe rate limits, configure your demo API key using the following environment variable:

```bash
export COINGECKO_API_KEY="your_api_key_here"

## Installation

```bash
git clone https://github.com/lyutskangeorgiev/crypto-cli.git
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
python -m crypto_cli.main price --coins bitcoin --vs usd
```

### Multiple coins:

```bash
python -m crypto_cli.main price --coins bitcoin,ethereum,solana --vs usd
```

### Multiple vs-currencies:

```bash
python -m crypto_cli.main price --coins bitcoin --vs usd,eur
```
