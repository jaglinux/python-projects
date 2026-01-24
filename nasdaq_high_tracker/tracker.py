#!/usr/bin/env python3
"""
Main tracker module for NASDAQ High Tracker.
Orchestrates snapshots, tracks history, and identifies high breakouts.
"""

import os
import argparse
from datetime import datetime, timezone, timedelta

import pandas as pd

import snapshot
import sentiment
import agent

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
HISTORY_FILE = os.path.join(OUTPUT_DIR, "stocks_at_highs.txt")
SNAPSHOT_FILE = os.path.join(OUTPUT_DIR, "snapshot.txt")


def load_history() -> pd.DataFrame:
    """Load historical data from CSV file."""
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE, parse_dates=["timestamp"])
    else:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "Ticker",
                "Name",
                "Price",
                "Market Cap (B)",
                "52W High",
                "52W Low",
                "% From 52W High",
                "All-Time High",
                "% From ATH",
                "At 52W High",
                "At ATH",
                "Sentiment",
                "Sentiment Score",
            ]
        )


def save_history(df_hist: pd.DataFrame):
    """Save historical data to CSV file."""
    df_hist.to_csv(HISTORY_FILE, index=False)


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
    numeric_cols = ["Price", "52W High", "% From 52W High", "All-Time High", "% From ATH"]
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


def latest_prices_by_ticker(df_hist: pd.DataFrame) -> pd.Series:
    """Get the latest price for each ticker from history."""
    if df_hist.empty:
        return pd.Series(dtype=float)
    df_sorted = df_hist.sort_values(["Ticker", "timestamp"])
    return df_sorted.groupby("Ticker")["Price"].last()


def prices_changed(df_snap: pd.DataFrame, last_prices: pd.Series) -> bool:
    """Check if any prices have changed since last snapshot."""
    if last_prices.empty:
        return True

    for _, row in df_snap.iterrows():
        ticker = row["Ticker"]
        new_price = row["Price"]
        old_price = last_prices.get(ticker, None)

        if pd.isna(new_price):
            continue

        if old_price is None or pd.isna(old_price):
            return True

        try:
            if abs(float(new_price) - float(old_price)) > 0.01:
                return True
        except Exception:
            return True

    return False


def detect_new_highs(df_hist: pd.DataFrame) -> pd.DataFrame:
    """
    Detect stocks that recently broke to new 52W highs or ATH.
    Returns DataFrame of breakout stocks.
    """
    if df_hist.empty:
        return pd.DataFrame()
    
    df_hist = df_hist.sort_values(["Ticker", "timestamp"])
    
    breakouts = []
    for ticker, g in df_hist.groupby("Ticker"):
        if len(g) < 2:
            continue
        
        g = g.reset_index(drop=True)
        current = g.iloc[-1]
        previous = g.iloc[-2]
        
        # Check if just broke to 52W high (wasn't at high, now is)
        new_52w = (
            current.get("At 52W High", False) == True and 
            previous.get("At 52W High", False) == False
        )
        
        # Check if just broke to ATH
        new_ath = (
            current.get("At ATH", False) == True and 
            previous.get("At ATH", False) == False
        )
        
        if new_52w or new_ath:
            breakouts.append({
                "Ticker": ticker,
                "Name": current.get("Name"),
                "Price": current["Price"],
                "New 52W High": new_52w,
                "New ATH": new_ath,
                "% From 52W High": current.get("% From 52W High"),
                "% From ATH": current.get("% From ATH"),
                "Sentiment": current.get("Sentiment"),
            })
    
    return pd.DataFrame(breakouts)


def compute_momentum(df_hist: pd.DataFrame) -> pd.DataFrame:
    """
    Compute daily and weekly price momentum for each ticker.
    Also tracks movement toward/away from highs.
    """
    df_hist = df_hist.sort_values(["Ticker", "timestamp"])
    
    results = []
    for ticker, g in df_hist.groupby("Ticker"):
        g = g.reset_index(drop=True)
        if len(g) == 0:
            continue

        last_row = g.iloc[-1]
        last_time = last_row["timestamp"]
        last_price = last_row["Price"]

        # Daily change
        daily_change = None
        if len(g) >= 2 and pd.notna(g["Price"].iloc[-2]) and pd.notna(last_price):
            prev_price = g["Price"].iloc[-2]
            if prev_price not in (None, 0):
                daily_change = (last_price / prev_price - 1) * 100

        # Weekly change (5 days)
        weekly_change = None
        cutoff_time = last_time - timedelta(days=5)
        weekly_candidates = g[g["timestamp"] <= cutoff_time]
        
        if not weekly_candidates.empty and pd.notna(last_price) and last_price not in (None, 0):
            weekly_row = weekly_candidates.iloc[-1]
            weekly_price = weekly_row["Price"]
            if pd.notna(weekly_price) and weekly_price not in (None, 0):
                weekly_change = (last_price / weekly_price - 1) * 100

        # Movement toward 52W high (positive = moving toward high)
        high_momentum = None
        if len(g) >= 2:
            prev_pct = g["% From 52W High"].iloc[-2]
            curr_pct = last_row.get("% From 52W High")
            if pd.notna(prev_pct) and pd.notna(curr_pct):
                high_momentum = curr_pct - prev_pct  # Positive = closer to high

        results.append({
            "Ticker": ticker,
            "Name": last_row.get("Name"),
            "Price": last_price,
            "Market Cap (B)": last_row.get("Market Cap (B)"),
            "Daily Change %": daily_change,
            "Weekly Change %": weekly_change,
            "% From 52W High": last_row.get("% From 52W High"),
            "% From ATH": last_row.get("% From ATH"),
            "High Momentum": high_momentum,
            "At 52W High": last_row.get("At 52W High"),
            "At ATH": last_row.get("At ATH"),
            "Sentiment": last_row.get("Sentiment"),
            "Sentiment Score": last_row.get("Sentiment Score"),
        })

    return pd.DataFrame(results)


def print_summary(df_momentum: pd.DataFrame, df_breakouts: pd.DataFrame):
    """Print a summary of the high tracker analysis."""
    print("\n" + "=" * 70)
    print("📊 NASDAQ HIGH TRACKER SUMMARY")
    print("=" * 70)
    
    # Stocks at or near 52W high
    at_52w = df_momentum[df_momentum["At 52W High"] == True]
    if not at_52w.empty:
        print(f"\n🔥 Stocks at 52-Week High ({len(at_52w)}):")
        for _, row in at_52w.iterrows():
            name = row.get('Name', '') or ''
            name_short = name[:25] + "..." if len(name) > 25 else name
            print(f"   {row['Ticker']:6} {name_short:28} ${row['Price']:8.2f}  "
                  f"({row['% From 52W High']:+.2f}%)")
    
    # Stocks at ATH
    at_ath = df_momentum[df_momentum["At ATH"] == True]
    if not at_ath.empty:
        print(f"\n🚀 Stocks at All-Time High ({len(at_ath)}):")
        for _, row in at_ath.iterrows():
            name = row.get('Name', '') or ''
            name_short = name[:25] + "..." if len(name) > 25 else name
            print(f"   {row['Ticker']:6} {name_short:28} ${row['Price']:8.2f}  "
                  f"({row['% From ATH']:+.2f}%)")
    
    # New breakouts
    if not df_breakouts.empty:
        print(f"\n⚡ NEW BREAKOUTS DETECTED:")
        for _, row in df_breakouts.iterrows():
            breakout_type = []
            if row.get("New 52W High"):
                breakout_type.append("52W High")
            if row.get("New ATH"):
                breakout_type.append("ATH")
            name = row.get('Name', '') or ''
            name_short = name[:25] + "..." if len(name) > 25 else name
            print(f"   {row['Ticker']:6} {name_short:28} ${row['Price']:8.2f}  "
                  f"→ New {', '.join(breakout_type)}!")
    
    # Top momentum stocks (moving toward highs)
    momentum_df = df_momentum[df_momentum["High Momentum"].notna()].copy()
    if not momentum_df.empty:
        top_momentum = momentum_df.nlargest(5, "High Momentum")
        print(f"\n📈 Top 5 Stocks Moving Toward Highs:")
        for _, row in top_momentum.iterrows():
            name = row.get('Name', '') or ''
            name_short = name[:25] + "..." if len(name) > 25 else name
            print(f"   {row['Ticker']:6} {name_short:28} ${row['Price']:8.2f}  "
                  f"Momentum: {row['High Momentum']:+.2f}%")
    
    print("\n" + "=" * 70)


def main(use_cache: bool = False):
    """
    Main execution function.
    
    Args:
        use_cache: If True, load from output/snapshot.txt instead of calling yfinance API.
    """
    print("=" * 70)
    print("🎯 NASDAQ HIGH TRACKER")
    print(f"   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    if use_cache:
        print("   [CACHE MODE - using saved snapshot]")
    print("=" * 70)
    
    # 1) Fetch price data
    if use_cache:
        print("\n=== Loading from cached snapshot ===")
        df_prices = load_snapshot_from_file()
    else:
        print("\n=== Fetching stock prices ===")
        df_prices = snapshot.main()

    # 2) Check if prices changed
    df_hist_before = load_history()
    last_prices = latest_prices_by_ticker(df_hist_before)

    if not prices_changed(df_prices, last_prices):
        print("\nNo price changes vs last stored snapshot; skipping update.")
        return

    # 3) Fetch sentiment only for stocks at 52W high or ATH
    high_stocks = df_prices[
        (df_prices["At 52W High"] == True) | (df_prices["At ATH"] == True)
    ]
    high_tickers = high_stocks["Ticker"].tolist()
    
    print(f"\n=== Fetching sentiment for {len(high_tickers)} stocks at highs ===")
    df_sentiment = sentiment.main(tickers=high_tickers)

    # 4) Merge price + sentiment data
    df_snap = df_prices.merge(df_sentiment, on="Ticker", how="left")

    # 5) Append to history
    now = datetime.now(timezone.utc)
    df_append = df_snap.copy()
    df_append["timestamp"] = now

    # Ensure all columns exist
    expected_cols = [
        "timestamp", "Ticker", "Name", "Price", "Market Cap (B)", "52W High", "52W Low",
        "% From 52W High", "All-Time High", "% From ATH", "At 52W High", 
        "At ATH", "Sentiment", "Sentiment Score"
    ]
    for col in expected_cols:
        if col not in df_append.columns:
            df_append[col] = pd.NA

    df_append = df_append[expected_cols]
    
    # Filter to only stocks at 52W high or ATH
    df_append = df_append[
        (df_append["At 52W High"] == True) | (df_append["At ATH"] == True)
    ]
    print(f"\n{len(df_append)} stocks at 52W high or ATH")
    
    df_hist_after = pd.concat([df_hist_before, df_append], ignore_index=True)
    
    # Create output directory if needed
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_history(df_hist_after)
    print(f"History saved to {HISTORY_FILE}")

    # 6) Detect breakouts
    df_breakouts = detect_new_highs(df_hist_after)

    # 7) Compute momentum
    df_momentum = compute_momentum(df_hist_after)

    # 8) Print summary
    print_summary(df_momentum, df_breakouts)

    # 9) Generate AI analysis
    agent.main(df_momentum, df_breakouts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NASDAQ High Tracker")
    parser.add_argument(
        "--use-cache", "-c",
        action="store_true",
        help="Use cached snapshot.txt instead of fetching from yfinance API"
    )
    args = parser.parse_args()
    
    main(use_cache=args.use_cache)
