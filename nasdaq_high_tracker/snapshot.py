#!/usr/bin/env python3
"""
Snapshot module for NASDAQ High Tracker.
Fetches current quotes, 52-week high, and all-time high data for S&P 500 stocks.
"""

import os
import yfinance as yf
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timezone

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TICKER_FILE = os.path.join(SCRIPT_DIR, "ticker.txt")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")


def load_tickers() -> list:
    """
    Load tickers from ticker.txt file (in same folder as this script).
    Exits with error if file doesn't exist.
    """
    if not os.path.exists(TICKER_FILE):
        print(f"Error: ticker.txt not found at {TICKER_FILE}")
        print(f"Run 'python fetch_tickers.py' first to generate the S&P 500 ticker list.")
        exit(1)
    
    with open(TICKER_FILE, "r", encoding="utf-8") as f:
        tickers = [line.strip() for line in f if line.strip()]
    
    if not tickers:
        print(f"Error: ticker.txt is empty.")
        exit(1)
    
    print(f"Loaded {len(tickers)} tickers from ticker.txt")
    return tickers


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
    company_name = None

    # Try fast_info first (faster)
    try:
        fi = t.fast_info
        price = getattr(fi, "last_price", None) or getattr(fi, "last_close", None)
        market_cap = getattr(fi, "market_cap", None)
        yr_high = getattr(fi, "year_high", None)
        yr_low = getattr(fi, "year_low", None)
    except Exception:
        pass

    # Get company name and fallback values from info
    try:
        info = t.info
        company_name = info.get("shortName") or info.get("longName")
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
        "Name": company_name,
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

    # Sort by: At 52W High (True first), then At ATH (True first), then % From 52W High
    df = df.sort_values(
        by=["At 52W High", "At ATH", "% From 52W High"],
        ascending=[False, False, False],
    )

    # Print table (selected columns for readability)
    display_cols = [
        "Ticker", "Name", "Price", "52W High", "% From 52W High", 
        "All-Time High", "% From ATH", "At 52W High", "At ATH"
    ]
    
    # Format table output
    table_output = tabulate(
        df[display_cols],
        headers="keys",
        tablefmt="github",
        showindex=False,
        floatfmt=".2f",
    )
    
    print("\n" + table_output)

    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Save to single output file (overwrite each time)
    output_file = os.path.join(OUTPUT_DIR, "snapshot.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"S&P 500 High Tracker Snapshot\n")
        f.write(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(f"Total stocks: {len(df)}\n")
        f.write("=" * 80 + "\n\n")
        f.write(table_output)
        f.write("\n")
    
    print(f"\nSaved to {output_file}")

    return df


if __name__ == "__main__":
    main()
