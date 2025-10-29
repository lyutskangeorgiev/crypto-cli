# Scope Validation - Crypto CLI

## Project Objective
Provide a lightweight command-line tool for fetching, storing, and analyzing cryptocurrency market data, focusing on Python skills, API handling, and data persistence.

---

## Must-Have Features
These are essential for achieving the project goals:

- **Fetch current cryptocurrency prices**  
  - Use public APIs to get real-time prices.
  - Core feature for learning API interaction.
- **Fetch historical price data**  
  - Support analysis over time periods.
  - Needed for plotting trends and testing data storage.
- **Charts and visualizations**  
  - Plot price trends or comparisons.
  - Useful for analysis, but optional.
- **Store data locally in SQLite**  
  - Ensures persistence between sessions.
  - Practice database integration in Python.
- **Basic CLI commands**  
  - Example: `get_price BTC`, `get_history ETH 7d`
  - Core for user interaction.

---

## Nice-to-Have Features
Optional features that enhance user experience but are not essential:

- **Sentiment analysis of crypto news**  
  - Analyze social media or news articles.
  - Adds complexity; can be added after core features.
- **Notifications for price changes**  
  - Send alerts when prices cross thresholds.
  - Peripheral feature; not required for core goals.

---

## Risks & Dependencies
Identify potential blockers and plan mitigations:

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits | High | Cache requests, throttle calls, or choose APIs with higher limits |
| Web scraping fragility | Medium | Prefer APIs over scraping; handle errors gracefully |
| Database constraints | Medium | Test schema with sample data; handle exceptions |
| Learning curve for new libraries | Low | Allocate extra time; use tutorials |
| Inconsistent data from APIs | Medium | Validate and clean data before storing |

---

## Validation Notes
- All **must-have features align with learning goals**: Python, APIs, data persistence.  
- Nice-to-have features **can be deferred** if timeline is tight.  
- Risks are documented with mitigations to **avoid surprises**.  
- Scope is **realistic and focused**; not overloaded with optional features.  

---

## Next Steps
1. Begin implementing must-have features first.  
2. Track any blockers in risk table.  
3. Reassess nice-to-have features after core functionality works.  
