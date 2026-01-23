#!/usr/bin/env python3
"""
Snapshot module for NASDAQ High Tracker.
Fetches current quotes, 52-week high, and all-time high data for S&P 500 stocks.
"""

import os
import yfinance as yf
import pandas as pd
import dataframe_image as dfi
from tabulate import tabulate
from datetime import datetime, timezone

TICKER_FILE = "ticker.txt"

# Fallback tickers if ticker.txt doesn't exist
DEFAULT_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    "AMD", "AVGO", "QCOM", "CRM", "ADBE", "NOW", "INTU",
]


def load_tickers() -> list:
    """
    Load tickers from ticker.txt file.
    Falls back to DEFAULT_TICKERS if file doesn't exist.
    """
    if os.path.exists(TICKER_FILE):
        with open(TICKER_FILE, "r", encoding="utf-8") as f:
            tickers = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(tickers)} tickers from {TICKER_FILE}")
        return tickers
    else:
        print(f"Warning: {TICKER_FILE} not found. Using default tickers.")
        print(f"Run 'python fetch_tickers.py' to generate the full S&P 500 list.")
        return DEFAULT_TICKERS


TICKERS = load_tickers()


def fetch_quote(ticker: str) -> dict:
    """
    Fetch current price, 52-week high, and all-time high for a ticker.
    Returns a dict with all relevant high-tracking metrics.
    """
    t = yf.Ticker(ticker)
    price = None
    market_cap = None
    yr_high = None
    yr_low = None
    all_time_high = None

    # Try fast_info first (faster)
    try:
        fi = t.fast_info
        price = getattr(fi, "last_price", None) or getattr(fi, "last_close", None)
        market_cap = getattr(fi, "market_cap", None)
        yr_high = getattr(fi, "year_high", None)
        yr_low = getattr(fi, "year_low", None)
    except Exception:
        pass

    # Fallback to info for missing values
    if price is None or market_cap is None or yr_high is None:
        try:
            info = t.info
            if price is None:
                price = info.get("regularMarketPrice")
            if market_cap is None:
                market_cap = info.get("marketCap")
            if yr_high is None:
                yr_high = info.get("fiftyTwoWeekHigh")
            if yr_low is None:
                yr_low = info.get("fiftyTwoWeekLow")
        except Exception:
            pass

    # Fetch all-time high from historical data (max available)
    try:
        hist = t.history(period="max")
        if not hist.empty:
            all_time_high = hist["High"].max()
    except Exception:
        pass

    # Calculate percentages from highs
    pct_from_52w_high = None
    pct_from_ath = None
    
    if price is not None and yr_high not in (None, 0):
        pct_from_52w_high = (price / yr_high - 1.0) * 100.0
    
    if price is not None and all_time_high not in (None, 0):
        pct_from_ath = (price / all_time_high - 1.0) * 100.0

    # Determine if at or near highs (within 2%)
    at_52w_high = pct_from_52w_high is not None and pct_from_52w_high >= -2.0
    at_ath = pct_from_ath is not None and pct_from_ath >= -2.0

    return {
        "Ticker": ticker,
        "Price": price,
        "Market Cap (B)": None if market_cap is None else market_cap / 1e9,
        "52W High": yr_high,
        "52W Low": yr_low,
        "% From 52W High": pct_from_52w_high,
        "All-Time High": all_time_high,
        "% From ATH": pct_from_ath,
        "At 52W High": at_52w_high,
        "At ATH": at_ath,
    }


def main() -> pd.DataFrame:
    """
    Fetch quotes for all tickers and return a DataFrame.
    Also exports a styled PNG table.
    """
    print(f"Fetching quotes for {len(TICKERS)} NASDAQ stocks...")
    
    rows = []
    for symbol in TICKERS:
        print(f"  {symbol}...", end=" ", flush=True)
        quote = fetch_quote(symbol)
        rows.append(quote)
        print("✓")

    df = pd.DataFrame(rows)

    # Sort by % from 52W High (closest to high first)
    df = df.sort_values(
        by="% From 52W High",
        key=lambda s: s.fillna(-999),
        ascending=False,
    )

    # Print table (selected columns for readability)
    display_cols = [
        "Ticker", "Price", "52W High", "% From 52W High", 
        "All-Time High", "% From ATH", "At 52W High", "At ATH"
    ]
    
    print("\n" + tabulate(
        df[display_cols],
        headers="keys",
        tablefmt="github",
        showindex=False,
        floatfmt=".2f",
    ))

    # Export PNG with styling
    styled = df[display_cols].style.format(
        {
            "Price": "{:.2f}",
            "52W High": "{:.2f}",
            "% From 52W High": "{:+.2f}%",
            "All-Time High": "{:.2f}",
            "% From ATH": "{:+.2f}%",
        },
        na_rep="N/A"
    ).applymap(
        lambda x: "background-color: #90EE90" if x == True else "",
        subset=["At 52W High", "At ATH"]
    ).hide(axis="index")
    
    dfi.export(styled, "nasdaq_highs_table.png")
    print("\nSaved nasdaq_highs_table.png")

    return df


if __name__ == "__main__":
    main()
