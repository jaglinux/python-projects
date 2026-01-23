#!/usr/bin/env python3
"""
Fetch all S&P 500 tickers from Wikipedia and save to ticker.txt.
Run this manually to update the ticker list.
"""

import pandas as pd


def fetch_sp500_tickers() -> list:
    """
    Fetch current S&P 500 constituents from Wikipedia.
    Returns list of ticker symbols.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    print("Fetching S&P 500 tickers from Wikipedia...")
    
    # Read the first table from the Wikipedia page
    tables = pd.read_html(url)
    df = tables[0]
    
    # The ticker column is named "Symbol"
    tickers = df["Symbol"].tolist()
    
    # Clean up tickers (some have dots like BRK.B, replace with dash for yfinance)
    tickers = [t.replace(".", "-") for t in tickers]
    
    print(f"Found {len(tickers)} tickers")
    
    return sorted(tickers)


def save_tickers(tickers: list, filename: str = "ticker.txt"):
    """Save tickers to a text file, one per line."""
    with open(filename, "w", encoding="utf-8") as f:
        for ticker in tickers:
            f.write(f"{ticker}\n")
    
    print(f"Saved {len(tickers)} tickers to {filename}")


def main():
    """Fetch S&P 500 tickers and save to file."""
    tickers = fetch_sp500_tickers()
    save_tickers(tickers)
    
    # Preview first 20
    print("\nFirst 20 tickers:")
    print(", ".join(tickers[:20]))


if __name__ == "__main__":
    main()
