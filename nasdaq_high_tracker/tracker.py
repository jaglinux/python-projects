#!/usr/bin/env python3
"""
Main tracker module for S&P 500 High Tracker.
Orchestrates snapshots, sentiment, and AI analysis.
"""

import os
import argparse
from datetime import datetime, timezone

import pandas as pd

import snapshot
import sentiment
import agent
import high_history

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
SNAPSHOT_FILE = os.path.join(OUTPUT_DIR, "snapshot.txt")


def load_snapshot_from_file() -> pd.DataFrame:
    """
    Load snapshot data from output/snapshot.txt file.
    Used for testing without making API calls to yfinance.
    """
    if not os.path.exists(SNAPSHOT_FILE):
        print(f"Error: {SNAPSHOT_FILE} not found.")
        print("Run 'python snapshot.py' first to generate the snapshot.")
        exit(1)
    
    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Find the table header line (starts with | Ticker)
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("| Ticker"):
            header_idx = i
            break
    
    if header_idx is None:
        print("Error: Could not find table header in snapshot.txt")
        exit(1)
    
    # Parse header
    header_line = lines[header_idx]
    headers = [h.strip() for h in header_line.split("|") if h.strip()]
    
    # Parse data rows (skip header and separator line)
    rows = []
    for line in lines[header_idx + 2:]:  # Skip header and |---|---| line
        if not line.strip() or not line.strip().startswith("|"):
            continue
        values = [v.strip() for v in line.split("|") if v.strip() != ""]
        if len(values) == len(headers):
            rows.append(values)
    
    df = pd.DataFrame(rows, columns=headers)
    
    # Convert numeric columns
    numeric_cols = ["Price", "52W High", "% From 52W High", "All-Time High", "% From ATH", "Market Cap (B)"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Convert boolean columns
    bool_cols = ["At 52W High", "At ATH"]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].str.strip().str.lower() == "true"
    
    print(f"Loaded {len(df)} stocks from {SNAPSHOT_FILE}")
    return df


def main(use_cache: bool = False, date_str: str = None, history_only: bool = False):
    """
    Main execution function.
    
    Args:
        use_cache: If True, load from output/snapshot.txt instead of calling yfinance API.
        date_str: Optional date string (YYYY-MM-DD) for tracking history.
        history_only: If True, only fetch prices and update high_history.json (skip sentiment/AI).
                      Useful for backfilling historical data.
    """
    # Use today's date if not specified
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    print("=" * 70)
    print("🎯 S&P 500 HIGH TRACKER")
    print(f"   Date: {date_str}")
    if use_cache:
        print("   [CACHE MODE - using saved snapshot]")
    if history_only:
        print("   [HISTORY ONLY MODE - skipping sentiment/AI]")
    print("=" * 70)
    
    # 1) Fetch price data
    if use_cache:
        print("\n=== Loading from cached snapshot ===")
        df_prices = load_snapshot_from_file()
    else:
        print("\n=== Fetching stock prices ===")
        df_prices = snapshot.main(date_str=date_str)

    # 2) Filter to stocks at 52W high or ATH
    df_highs = df_prices[
        (df_prices["At 52W High"] == True) | (df_prices["At ATH"] == True)
    ].copy()
    
    print(f"\n{len(df_highs)} stocks at 52W high or ATH")
    
    if df_highs.empty:
        print("No stocks at highs for this date.")
        # Still update history (empty update preserves existing data)
        high_history.update_history(df_highs, date_str)
        return

    # 3) Update high history tracker (do this early for history_only mode)
    print("\n=== Updating high history ===")
    history = high_history.update_history(df_highs, date_str)
    
    # Show top hitters
    df_history = high_history.get_summary(history)
    if not df_history.empty:
        top_5 = df_history.head(5)
        print(f"Top 5 frequent high hitters:")
        for _, row in top_5.iterrows():
            print(f"   {row['Ticker']:6} - {row['Hit Count']} hits (last: {row['Last Date']})")
    
    print(f"\nHigh history saved to output/high_history.json and output/high_history.txt")
    
    # If history_only mode, stop here
    if history_only:
        print("\n✅ History updated. Skipping sentiment and AI analysis.")
        return

    # 4) Fetch sentiment for stocks at highs
    high_tickers = df_highs["Ticker"].tolist()
    print(f"\n=== Fetching sentiment for {len(high_tickers)} stocks ===")
    df_sentiment = sentiment.main(tickers=high_tickers)

    # 5) Merge price + sentiment data
    df_merged = df_highs.merge(df_sentiment, on="Ticker", how="left")
    
    # 6) Print summary
    print("\n" + "=" * 70)
    print("📊 STOCKS AT HIGHS SUMMARY")
    print("=" * 70)
    
    at_ath = df_merged[df_merged["At ATH"] == True]
    at_52w_only = df_merged[(df_merged["At 52W High"] == True) & (df_merged["At ATH"] == False)]
    
    print(f"\n🏆 At All-Time High: {len(at_ath)} stocks")
    print(f"🔥 At 52-Week High (not ATH): {len(at_52w_only)} stocks")
    print(f"📈 Total at highs: {len(df_merged)} stocks")
    
    # Count by sentiment
    if "Sentiment" in df_merged.columns:
        bullish = len(df_merged[df_merged["Sentiment"] == "Bullish"])
        neutral = len(df_merged[df_merged["Sentiment"] == "Neutral"])
        bearish = len(df_merged[df_merged["Sentiment"] == "Bearish"])
        print(f"\n📰 Sentiment: Bullish={bullish}, Neutral={neutral}, Bearish={bearish}")
    
    print("=" * 70)

    # 7) Generate AI analysis
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    agent.main(df_merged)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="S&P 500 High Tracker")
    parser.add_argument(
        "--use-cache", "-c",
        action="store_true",
        help="Use cached snapshot.txt instead of fetching from yfinance API"
    )
    parser.add_argument(
        "--date", "-d",
        type=str,
        default=None,
        help="Date for tracking (YYYY-MM-DD). Defaults to today."
    )
    parser.add_argument(
        "--history-only", "-H",
        action="store_true",
        help="Only update high_history.json (skip sentiment and AI analysis). Useful for backfilling."
    )
    args = parser.parse_args()
    
    main(use_cache=args.use_cache, date_str=args.date, history_only=args.history_only)
