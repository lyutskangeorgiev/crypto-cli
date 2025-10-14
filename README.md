# Crypto CLI

A command-line tool for fetching, storing, and analyzing cryptocurrency market data.  
Built with Python, it allows users to query real-time prices, retrieve historical OHLCV data, and track trending coins.

---

## Features

- Fetch real-time price for any supported cryptocurrency  
- Retrieve historical OHLCV (Open, High, Low, Close, Volume) data  
- Display trending news in the world of cryptocurrencies  
- Save data locally in a SQLite database  

---

## Prerequisites

- Python 3.10 or higher  
- Internet connection for API requests  

---

## Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/lyutskangeorgiev/crypto-cli.git
cd crypto-cli
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Data Sources & Dependencies

This project relies on:

- [CoinGecko API](https://www.coingecko.com/en/api) for real-time and historical cryptocurrency data
- Python libraries: `pycoingecko`, `requests`, `BeautifulSoup`, `pandas`, `Typer`, `sqlite3`
- Optional news scraping from sites like CoinDesk, Cointelegraph

## Usage

### Commands

- `price <coin>`  
  Fetch current price, market cap, and 24h volume for a specific coin.

- `history <coin> --days <n>`  
  Retrieve historical OHLCV data for the past `n` days.

- `trending`  
  Display trending news in the world of cryptocurrencies.

### Examples

```bash
python cli.py price bitcoin
python cli.py history ethereum --days 30
python cli.py trending
```

### Sample Output

**Price Example:**

Bitcoin (BTC): $63,250 | Market Cap: $1.2T | 24h Volume: $32B

**Historical Data Example:**

| Date       | Open    | High    | Low     | Close   | Volume |
|------------|---------|---------|---------|---------|--------|
| 2025-08-09 | 3,100.5 | 3,150.2 | 3,080.1 | 3,125.4 | 1.2B   |
| 2025-08-10 | 3,125.4 | 3,180.0 | 3,110.0 | 3,172.5 | 1.3B   |

**Trending Example:**

1. Solana (SOL)
2. Avalanche (AVAX)
3. Polkadot (DOT)

---

## Data Storage

All historical and fetched data is stored locally in a SQLite database (`crypto_data.db` by default).

---

## Running Tests

Make sure your virtual environment is activated, then run:

```bash
pytest tests/
```
