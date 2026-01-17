# snapshot.py
import yfinance as yf
import pandas as pd
import dataframe_image as dfi
from tabulate import tabulate

TICKERS = [
    "DUOL", "HUBS", "MNDY", "TEAM", "GTLB", "KVYO", "NOW", "CSU.TO",
    "DDOG", "CRM", "ADBE", "WDAY", "INTU", "FICO", "PATH", "ADSK",
    "ZETA", "MSFT", "PLTR", "MDB", "FIG",
]

def fetch_quote(ticker: str):
    t = yf.Ticker(ticker)
    price = None
    market_cap = None
    yr_high = None

    # fast_info path (faster, has year_high in recent versions)[web:128]
    try:
        fi = t.fast_info
        price = getattr(fi, "last_price", None) or getattr(fi, "last_close", None)
        market_cap = getattr(fi, "market_cap", None)
        yr_high = getattr(fi, "year_high", None)
    except Exception:
        pass

    # fallback to info
    if price is None or market_cap is None or yr_high is None:
        try:
            info = t.info
            if price is None:
                price = info.get("regularMarketPrice")
            if market_cap is None:
                market_cap = info.get("marketCap")
            if yr_high is None:
                yr_high = info.get("fiftyTwoWeekHigh")  # standard key[web:72][web:123]
        except Exception:
            pass

    # % below 52-week high (negative if below)
    pct_from_high = None
    if price is not None and yr_high not in (None, 0):
        pct_from_high = (price / yr_high - 1.0) * 100.0

    return price, market_cap, yr_high, pct_from_high

def main() -> pd.DataFrame:
    rows = []
    for symbol in TICKERS:
        price, mcap, yr_high, pct_from_high = fetch_quote(symbol)
        rows.append(
            {
                "Ticker": symbol,
                "Price": price,
                "Market Cap (B)": None if mcap is None else mcap / 1e9,
                "52W High": yr_high,
                "% From 52W High": pct_from_high,
            }
        )

    df = pd.DataFrame(rows)

    # sort by market cap ascending (None goes last)
    df = df.sort_values(
        by="Market Cap (B)",
        key=lambda s: s.fillna(s.max() + 1),
        ascending=True,
    )

    # pretty print to terminal
    print(
        tabulate(
            df,
            headers="keys",
            tablefmt="github",
            showindex=False,
            floatfmt=".2f",
        )
    )

    # style for image
    styled = df.style.format(
        {
            "Price": "{:.2f}",
            "Market Cap (B)": "{:.2f}",
            "52W High": "{:.2f}",
            "% From 52W High": "{:.2f}",
        }
    ).hide(axis="index")

    # export to PNG
    dfi.export(styled, "stocks_table.png")
    print("Saved stocks_table.png – share this image on WhatsApp.")

    return df

if __name__ == "__main__":
    main()
