#!/usr/bin/env python3

import yfinance as yf
import pandas as pd
import dataframe_image as dfi
from tabulate import tabulate
from pathlib import Path

def load_tickers(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Ticker file not found: {path}")

    tickers: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        tickers.extend([item.strip() for item in value.split(",") if item.strip()])
    return tickers

def fetch_quote(ticker: str):
    t = yf.Ticker(ticker)
    company = ticker
    price = None
    market_cap = None
    yr_high = None

    # fast_info first
    try:
        fi = t.fast_info
        price = getattr(fi, "last_price", None) or getattr(fi, "last_close", None)
        market_cap = getattr(fi, "market_cap", None)
        yr_high = getattr(fi, "year_high", None)
    except Exception:
        pass

    # fallback to info
    if price is None or market_cap is None or yr_high is None or company == ticker:
        try:
            info = t.info
            if company == ticker:
                company = (
                    info.get("shortName")
                    or info.get("longName")
                    or info.get("displayName")
                    or ticker
                )
            if price is None:
                price = info.get("regularMarketPrice")
            if market_cap is None:
                market_cap = info.get("marketCap")
            if yr_high is None:
                yr_high = info.get("fiftyTwoWeekHigh")
        except Exception:
            pass

    pct_from_high = None
    if price is not None and yr_high not in (None, 0):
        pct_from_high = (price / yr_high - 1.0) * 100.0

    return company, price, market_cap, yr_high, pct_from_high

def main() -> pd.DataFrame:
    ticker_file = Path(__file__).with_name("ticker.txt")
    tickers = load_tickers(ticker_file)

    rows = []
    for symbol in tickers:
        company, price, mcap, yr_high, pct_from_high = fetch_quote(symbol)
        rows.append(
            {
                "Ticker": symbol,
                "Company": company,
                "Price": price,
                "Market Cap (B)": None if mcap is None else mcap / 1e9,
                "52W High": yr_high,
                "% From 52W High": pct_from_high,
            }
        )

    df = pd.DataFrame(rows)

    # sort by market cap ascending
    df = df.sort_values(
        by="Market Cap (B)",
        key=lambda s: s.fillna(s.max() + 1),
        ascending=True,
    )

    # print table
    print(
        tabulate(
            df,
            headers="keys",
            tablefmt="github",
            showindex=False,
            floatfmt=".2f",
        )
    )

    # export PNG
    styled = df.style.format(
        {
            "Price": "{:.2f}",
            "Market Cap (B)": "{:.2f}",
            "52W High": "{:.2f}",
            "% From 52W High": "{:.2f}",
        }
    ).hide(axis="index")
    dfi.export(styled, "stocks_table.png")
    print("Saved stocks_table.png – share this image on WhatsApp.")

    return df

if __name__ == "__main__":
    main()
