
---

# 📐 DESIGN.md (Annotated Example for Crypto CLI)


# Crypto CLI - Design Document

## 1. Introduction
The project aims to provide a lightweight CLI for cryptocurrency research.  
It focuses on simple data acquisition, local storage, and analytical features without needing a web interface.

---

## 2. Architecture Overview
- **CLI Layer**: Built with Typer, defines commands (`price`, `history`, `trending`).  
- **Data Acquisition**: Uses CoinGecko API (pycoingecko) for prices and history, web scraping for news.  
- **Persistence**: SQLite database for local storage.  
- **Analysis**: Pandas for computing returns, drawdowns, etc.  

---

## 3. Technology Stack
- **Python 3.11**  
- **CLI Framework:** Typer (chosen for type-hint support & auto-docs)  
- **Data:** pycoingecko, requests + BeautifulSoup  
- **Database:** SQLite (chosen for simplicity; future upgrade to PostgreSQL possible)  
- **Analysis:** pandas  
- **Testing:** pytest  

---

## 4. Data Flow
Example: `cli.py history bitcoin --days 30`

1. CLI parses command arguments.  
2. Fetch module calls CoinGecko API.  
3. Response JSON is converted into a pandas DataFrame.  
4. Data is stored in SQLite (if user requests).  
5. CLI displays results in a formatted table.  

---

## 5. Error Handling
- API unavailable → retry logic, user-friendly error message.  
- Invalid coin symbol → suggest closest matches.  
- Database write error → fallback to in-memory DataFrame.  

---

## 6. Testing Strategy
- **Unit Tests**: API fetch, database insert, analysis functions.  
- **Integration Tests**: CLI commands with Typer’s CliRunner.  
- **End-to-End Tests**: Fetch + store + query cycle.  

---

## 7. Future Enhancements
- Async requests (aiohttp) for faster data fetching  
- On-chain analytics (Glassnode API)  
- Backtesting engine  
- REST API + Web dashboard

---
