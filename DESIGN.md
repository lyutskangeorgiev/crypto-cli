# crypto-cli Design Document

## 1. System Overview
`crypto-cli` is a lightweight, command-line interface application built in Python (>=3.10) to query and display cryptocurrency data. The tool leverages the CoinGecko API to provide real-time market data directly in the terminal, utilizing the `Typer` library for command parsing and `requests` for robust HTTP communications. 

## 2. Core Architecture
The project is modularized into distinct layers separating the CLI interface, API interaction, and utility helpers:

* **CLI Layer (`src/crypto_cli/main.py`)**: Acts as the entry point. It defines the Typer application, global configurations, and the available commands (`price`, `history`, `trending`). It handles user input, argument parsing, and top-level error reporting.
* **API Layer (`src/crypto_cli/api/`)**: Contains logic for communicating directly with the external API (CoinGecko). E.g., `fetch_market.py` handles the building and execution of the spot price queries.
* **Utility Layer (`src/crypto_cli/utils/`)**: 
    * `_session.py`: Manages the HTTP session, including retry adapters and custom headers.
    * `parse.py`: Validates and sanitizes user input.
    * `http_errors.py`: Categorizes HTTP response codes into semantic groups.

## 3. Data Flow
1.  **Initialization**: The CLI boots up and a global `Config` object is instantiated, capturing timeouts, API keys, and user-agent details.
2.  **Input Parsing**: User inputs (e.g., `--coins`, `--vs`) are passed through `parse.py` to ensure they meet regex requirements and size limits (maximum 10 items).
3.  **HTTP Request**: A configured `requests.Session` sends the query to the CoinGecko API.
4.  **Error Handling & Mapping**: Responses are evaluated. If an HTTP error occurs, `http_errors.py` categorizes it (INPUT, RATE, SERVER, OTHER) so `main.py` can display a user-friendly terminal message and exit cleanly without a raw traceback.
5.  **Output**: Successful JSON payloads are parsed and displayed (using libraries like `tabulate` and `rich`).

## 4. Command Specifications

### 4.1 Implemented Commands
* **`price`**: Fetches the current spot price for one or more cryptocurrencies.
    * **Arguments/Flags**: 
        * `--coins`: Comma-separated list of coin IDs (e.g., `bitcoin,ethereum`).
        * `--vs`: Comma-separated list of target fiat/crypto currencies (e.g., `usd,eur`).
        * `--mcap`: Boolean flag to include market capitalization.
        * `--vol`: Boolean flag to include 24-hour volume.
        * `--change`: Boolean flag to include 24-hour price change.
        * `--updated`: Boolean flag to include the last updated timestamp.

### 4.2 Planned Commands (Stubbed)
* **`history`**: Will fetch historical OHLCV (Open, High, Low, Close, Volume) data. Planned to support daily returns, CAGR (Compounded Annual Growth Rate), and Max Drawdown calculations.
* **`trending`**: Will fetch trending news or top trending coins from the cryptocurrency ecosystem.

## 5. HTTP Client & Networking
The application features a resilient HTTP layer configured to gracefully handle the unreliability of public APIs:
* **Session Management**: A persistent `requests.Session` is utilized for connection pooling.
* **Timeouts**: Explicit connect and read timeouts (defaulting to 3.0s and 10.0s respectively) prevent hanging queries.
* **Retry Strategy**: A `urllib3.Retry` adapter is mounted for the CoinGecko domain. It features an exponential backoff strategy for status codes `429` (Rate Limited) and `500, 502, 503, 504` (Server Errors).
* **Headers**: Injects a custom `User-Agent` and maps the `COINGECKO_API_KEY` to the `x-cg-demo-api-key` header.

## 6. Input Validation Strategy
Strict validation is enforced *before* network calls are made:
* **Coin IDs**: Must match regex `^[a-z0-9]+(?:-[a-z0-9]+)*$` (lowercase alphanumeric with optional hyphens).
* **VS Currencies**: Must match regex `^[a-z]{2,}$` (at least two lowercase alphabetical characters).
* **Limits**: Both inputs are capped at a maximum of 10 items to prevent abuse and adhere to API URL length constraints.

## 7. Future Roadmap
* **Caching**: Local disk caching for repeated queries to minimize API rate limit consumption.
* **Data Transformation**: Implementation of a dedicated `data/` module (e.g., `transform.py` and `analytics.py`) to process raw API JSON into pandas DataFrames for advanced calculations in the `history` command.
* **Persistence**: Placeholder `db.py` modules suggest future integration of local SQLite storage for user history or offline analytics.
