# Crypto CLI

A command-line tool for fetching, storing, and analyzing cryptocurrency market data.  
Built with Python, it helps users query real-time prices, retrieve historical data, and track trending coins.

# Features
- Fetch real-time price for any supported cryptocurrency  
- Retrieve historical OHLCV (Open, High, Low, Close, Volume) data  
- Display trending cryptocurrencies  
- Save data locally in a SQLite database  

# Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/lyutskangeorgiev/crypto-cli.git
cd crypto-cli
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

# Example usage:

```bash
python cli.py price bitcoin
python cli.py history ethereum --days 30
python cli.py trending
```

# Example output:

Bitcoin (BTC): $63,250 | Market Cap: $1.2T | 24h Volume: $32B
   
| Date       | Open   | High   | Low    | Close  | Volume |
|------------|--------|--------|--------|--------|--------|
| 2025-08-09 | 3100.5 | 3150.2 | 3080.1 | 3125.4 | 1.2B   |
| 2025-08-10 | 3125.4 | 3180.0 | 3110.0 | 3172.5 | 1.3B   |
   ...
   
   
1. Solana (SOL)
2. Avalanche (AVAX)
3. Polkadot (DOT)

# Running tests:

```bash
pytest tests/
