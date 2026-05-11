import re
import datetime

def parse_csv_ids(csv: str) -> list[str]:
    """Parse 'a,b,c' into normalized coin IDs (trim, lowercase, dedupe)."""
    formatted_csv = csv.split(',')
    result: list[str] = []

    for token in formatted_csv:
        formatted_token = token.strip().lower()
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", formatted_token):
            raise ValueError(f"invalid id '{formatted_token!r}'. use lowercase letters, digits, and hyphens")
        result.append(formatted_token)
    if len(result) == 0:
        #case for empty coins list
        # in CLI layer: except ValueError as e: raise typer.BadParameter(str(e))
        raise ValueError("coin ids cannot be empty")
    elif len(result) > 10:
        #case for above limit coins
        #in CLI layer: except ValueError as e: raise typer.BadParameter(str(e))
        raise ValueError("coin ids must be ≤ 10")
    return result

def parse_csv_vs(csv: str) -> list[str]:
    """Parse 'a,b,c' into normalized currencies (trim, lowercase, dedupe)."""
    formatted_csv = csv.split(',')
    result: list[str] = []
    for currency in formatted_csv:
        formatted_currency = currency.strip().lower()
        if not formatted_currency:
            continue
        if not re.fullmatch(r"[a-z]{2,}", formatted_currency):
            raise ValueError(f"invalid vs currency '{formatted_currency!r}'. use lowercase codes like 'usd','eur','btc'")

        result.append(formatted_currency)
    if len(result) > 10:
        raise ValueError("vs currencies must be ≤ 10")
    # in CLI layer: except ValueError as e: raise typer.BadParameter(str(e))
    if not result:
        raise ValueError("vs currencies cannot be empty")
    return result

def bool_to_str(flag: bool) -> str:
    """Return 'true' or 'false' for query strings."""
    if flag:
        return "true"
    else:
        return "false"

#if adding another endpoint move to a build_params func
#def build_params() -> dict:
#
#    join lists into comma strings
#    convert bools with as_bool_str(...)

def parse_date(date: str) -> datetime.date | None:
    """Parse 'date' into datetime object."""
    try:
        string_date = datetime.date.fromisoformat(date.strip())
        return string_date
    except ValueError as e:
        print(f"Invalid date: {e}")

def validate_date_range(start: datetime.date, end: datetime.date) -> tuple[datetime.date, datetime.date]:
    """Validate 'start' and 'end' dates."""
    if start > end:
        raise ValueError(f"Start date must be before end date: {start!r}")
    if end - start > datetime.timedelta(days= 5*365):
        raise ValueError(f"Cannot access data from more than 5 years back")
    else:
        return start, end

def date_range_to_unix(start: datetime.date, end: datetime.date) -> tuple[float, float]:
    """Return unix timestamp between 'start' and 'end' dates."""
    start_datetime = datetime.datetime(start.year, start.month, start.day)
    end_datetime = datetime.datetime(end.year, end.month, end.day)
    return start_datetime.timestamp(), end_datetime.timestamp()

def format_price(price: float) -> str:
    """Format price's floating-point representation dynamically."""
    if price == 0.0:
        return "0.00"
    #if bigger than 1 -> normal 2 after decimal
    elif price >= 1.0:
        return f"{price:,.2f}"
    #if price is less than 1 we go in 15 points precision with cutting off the trailing 0s
    else:
        price_formatted = f"{price:.15f}".rstrip('0')
        return price_formatted

def normalize_price(data: dict, coins_ids:list[str], vs_list: list[str],
                    include_marketcap: bool, include_24h_vol: bool,
                    include_24h_change: bool, include_last_updated: bool
                   ) -> list[dict]:
    """"Normalize price data."""
    rows = []
    for coin_id in coins_ids:
        for vs in vs_list:
            raw_price = float(data[coin_id].get(vs))
            #here make adapting float formatting for price
            price_str = format_price(raw_price)
            row = {
                "coin_id": coin_id,
                "currency": vs,
                "price": price_str
            }
            if include_marketcap:
                raw_mcap = float(data[coin_id][f"{vs}_market_cap"])
                row["mcap"] = f"{raw_mcap:.2f}"
            if include_24h_vol:
                raw_vol = float(data[coin_id][f"{vs}_24h_vol"])
                row["vol"] = f"{raw_vol:.2f}"
            if include_24h_change:
                raw_change = float(data[coin_id][f"{vs}_24h_change"])
                row["change"] = f"{raw_change:.2f}"
            if include_last_updated:
                sec = data[coin_id]["last_updated_at"]
                start_date = datetime.datetime(1970, 1, 1, 0, 0, 0)
                new_date = start_date + datetime.timedelta(seconds=sec)
                row["updated"] = new_date.isoformat()
            rows.append(row)

    return rows

