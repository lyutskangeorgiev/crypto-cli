import requests
from crypto_cli.utils.parse import bool_to_str

#func that makes the request:
def get_simple_price(api_base, connect_timeout,
                     read_timeout,
                     coin_ids, vs_currencies,
                     include_market_cap, include_24h_vol,
                     include_24h_change, include_last_updated,
                     session
) -> dict:
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": ",".join(vs_currencies),
        "include_market_cap": bool_to_str(include_market_cap),
        "include_24hr_vol": bool_to_str(include_24h_vol),
        "include_24hr_change": bool_to_str(include_24h_change),
        "include_last_updated_at": bool_to_str(include_last_updated)
    }
    url = f"{api_base}/simple/price"
    timeout = (connect_timeout, read_timeout)
    try:
        resp = session.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.ConnectTimeout as e: #so we dont lose the original traceback exception type
        raise RuntimeError("Connection timed out(check network)") from e
    except requests.exceptions.ReadTimeout as e:
        raise RuntimeError("Reading timed out(slow server or large response)") from e
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError("Connection error (DNS/TLS/socket)") from e
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 400:
            raise RuntimeError("Bad request (check params)") from e
        if status == 401 or status == 403:
            raise RuntimeError("Auth/plan error: check CoinGecko Pro API key/plan") from e
        if status == 404:
            raise RuntimeError("Unknown coind ID or endpoint path") from e
        if status == 429:
            raise RuntimeError("Too many requests for the API rate limit (check network)") from e
        if 500 <= status <= 599:
            raise RuntimeError("Server error at CoinGecko, try again later") from e
    try:
        return resp.json()

    except requests.exceptions.JSONDecodeError as e:
        if not resp.content.strip():
            raise RuntimeError("CoinGecko API response is empty (expected JSON)") from e
        ctype = resp.headers.get("Content-Type", "")#this can return None thats why -> ,""
        if ctype.lower().startswith("application/json"):
            raise RuntimeError("JSON but could not be parsed") from e

        raise RuntimeError(f"API returned non-JSON content (Content-Type: {ctype})") from e
