import re

def parse_csv_ids(csv: str) -> list[str]:
    """Parse 'a,b,c' into normalized coin IDs (trim, lowercase, dedupe)."""
    formatted_csv = csv.split(',')
    result: list[str] = []
    seen = set()
    for token in formatted_csv:
        formatted_token = token.strip().lower()
        if not formatted_token or formatted_token in seen:
            continue
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", formatted_token):
            raise ValueError(f"invalid id '{formatted_token!r}'. use lowercase letters, digits, and hyphens")

        seen.add(formatted_token)
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
    seen = set()
    for currency in formatted_csv:
        formatted_currency = currency.strip().lower()
        if not formatted_currency:
            continue
        if formatted_currency in seen:
            continue
        if not re.fullmatch(r"[a-z]{2,}", formatted_currency):
            raise ValueError(f"invalid vs currency '{formatted_currency!r}'. use lowercase codes like 'usd','eur','btc'")

        seen.add(formatted_currency)
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