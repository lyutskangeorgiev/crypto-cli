#used typer for CLI
#installed typer-completion for auto-completion of commands!
import typer
import requests

from dataclasses import dataclass, field

from click import BadParameter

from crypto_cli.utils._session import build_session
from crypto_cli.utils.http_errors import classify_http, Category
from crypto_cli.utils.parse import parse_csv_ids, parse_csv_vs
from crypto_cli.api.fetch_market import get_simple_price
app = typer.Typer(help= "Crypto Data CLI")

@dataclass
class Config: #for config of settings for the whole app
    api_base: str
    connect_timeout: float
    read_timeout: float
    db_path: str
    verbose: bool
    user_agent: str
    api_key: str|None = field(default=None, repr=False)#hide in print

@app.callback()
def main(ctx: typer.Context = typer.Option(None, hidden=True),
         api_base: str = typer.Option("https://api.coingecko.com/api/v3"),
         connect_timeout: float = typer.Option(3.0, "--connect-timeout", help="Connect timeout (s)"),
         read_timeout: float = typer.Option(10.0, "--read-timeout", help="Read timeout (s)"),
         db: str = typer.Option("src/db.py"),
         verbose: bool = typer.Option(False, "--verbose", "--v"),
         user_agent: str = typer.Option(
             "crypto-cli/0.1 (+https://github.com/lyutskangeorgiev/crypto-cli)",
             "--user-agent",
             "--ua",
             help="HTTP User-Agent to send"
         ),
         api_key: str|None = typer.Option(None, envvar=
            "COINGECKO_API_KEY", help="Coingecko demo API key (env: COINGECKO_API_KEY)")
):
    """Parse global options and stash config on ctx.obj."""
    config = Config(api_base=api_base, connect_timeout=connect_timeout, read_timeout=read_timeout, db_path=db, verbose=verbose, user_agent=user_agent, api_key=api_key)
    session = build_session(config)
    ctx.obj = {"config": config, "session": session}

#reusable for other commands
def _dbg_suffix(debug: dict | None) -> str:
    if not debug:
        return ""
    parts = []

    rid = str(debug.get("request_id", "")).strip()[:24]
    if rid:
        parts.append(f"rid={rid}")

    took_ms = debug.get("elapsed_ms")
    if took_ms is not None:
        try:
            parts.append(f"{int(took_ms)}ms")
        except Exception:
            pass

    excerpt = debug.get("resp_excerpt")
    if excerpt:
        #split to have each word - getting rid of weird spaces, new lines etc
        #then join with a space so u have normal word + space
        excerpt = " ".join(str(excerpt).split())[:80]
        parts.append(f"resp='{excerpt}'")

    if parts:
        return " " + " ".join(parts) #leading with space beacause
        # we attatch that to the error msg
    else:
        return ""

@app.command()
def price(
        coins: str = typer.Option(..., "--coins", help='CSV style of coingecko IDs(max 10), e.g. "bitcoin,ethereum"'),
        vs: str = typer.Option("usd", "--vs", help='CSV style of vs currencies (max 10), e.g. "usd,eur"'),
        mcap: bool = typer.Option(False, "--mcap", help="Add market cap"),
        vol: bool = typer.Option(False, "--vol", help="Add volume"),
        change: bool = typer.Option(False, "--change", help="Add 24hr change"),
        updated: bool = typer.Option(False, "--updated", help="Add timestamp of last update"),
        ctx: typer.Context = typer.Option(None)
):
    """CLI handler: parse inputs, call service, print result."""
    #take the cfg settings from ctx.obj
    cfg = ctx.obj["config"]
    ses = ctx.obj["session"]
    try:
        coin_ids = parse_csv_ids(coins)
    except ValueError as e:
        raise typer.BadParameter(str(e), param_hint="--coins")
    try:
        vs_list = parse_csv_vs(vs)
    except ValueError as e:
        raise typer.BadParameter(str(e), param_hint="--vs")
    #call fetch_market.py, passing cfg and flags (api)
    try:
        data,debug = get_simple_price(
            api_base=cfg.api_base,
            connect_timeout=cfg.connect_timeout,
            read_timeout=cfg.read_timeout,
            coin_ids=coin_ids,
            vs_currencies=vs_list,
            include_market_cap=mcap,
            include_24h_vol=vol,
            include_24h_change=change,
            include_last_updated=updated,
            session=ses
        )
    except requests.exceptions.HTTPError as e:
        msg = None
        if getattr(e, "response", None):
            status = e.response.status_code
        else:
            status = None
        catg = classify_http(status)
        if catg is Category.INPUT:
            if len(coin_ids) == 1 and status == 404:
                msg = f"unknown coin id {coin_ids[0]!r}"
                BadParameter(msg)
            else:
                msg = "input error. check coin ids and vs currencies"
                BadParameter(msg)

        elif catg is Category.RATE:
            msg = "rate limit. try again later"
            typer.echo(msg, err=True)
            raise typer.Exit(1)

        elif catg is Category.SERVER:
            msg = "service unavailable. try again later"
            typer.echo(msg, err=True)
            raise typer.Exit(1)

        elif catg is Category.OTHER:
            if status is not None:
                msg = f"http error ({status})"
            else:
                msg = "http error"
            typer.echo(msg, err=True)
            raise typer.Exit(1)

        if cfg.verbose:
            msg += _dbg_suffix(debug)
        typer.echo(msg, err=True)
        raise typer.Exit(1)

# pretty print result

@app.command()
def history():
    """
    Get historical data for a specific cryptocurrency.
    """
    print("history")

@app.command()
def trending():
    """
    Get trending news from the cryptocurrency world.
    (Will be implemented in other iteration of this project.)
    """
    print("trending")

if __name__ == "__main__":
    app()