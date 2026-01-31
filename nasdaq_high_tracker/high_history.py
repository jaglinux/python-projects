#!/usr/bin/env python3
"""
High History Tracker - Tracks how many times each stock hits 52W high or ATH.
Stores: ticker -> {count, last_2_dates}
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List

import pandas as pd

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
HISTORY_FILE = os.path.join(OUTPUT_DIR, "high_history.json")


def load_history() -> Dict:
    """Load the high history from JSON file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(history: Dict):
    """Save the high history to JSON file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def save_history_readable(history: Dict = None):
    """
    Save a human-readable text file of high history with tabular format.
    High hitters at the top.
    """
    from tabulate import tabulate
    
    if history is None:
        history = load_history()
    
    if not history:
        return
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "high_history.txt")
    
    # Build rows sorted by hit count
    rows = []
    for ticker, data in history.items():
        dates = data.get("dates", [])
        last_date = dates[-1] if len(dates) >= 1 else ""
        second_last = dates[-2] if len(dates) >= 2 else ""
        third_last = dates[-3] if len(dates) >= 3 else ""
        
        rows.append({
            "Ticker": ticker,
            "Name": data.get("name", "")[:30],  # Truncate long names
            "Hits": data.get("count", 0),
            "Last Hit": last_date,
            "2nd Last": second_last,
            "3rd Last": third_last
        })
    
    # Sort by hits descending
    rows.sort(key=lambda x: x["Hits"], reverse=True)
    
    # Add rank
    for i, row in enumerate(rows, 1):
        row["#"] = i
    
    # Reorder columns
    df = pd.DataFrame(rows)
    df = df[["#", "Ticker", "Name", "Hits", "Last Hit", "2nd Last", "3rd Last"]]
    
    # Create table
    table = tabulate(df, headers="keys", tablefmt="github", showindex=False)
    
    # Write file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("S&P 500 Momentum Tracker - High History\n")
        f.write(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write("=" * 90 + "\n\n")
        f.write("Stocks ranked by number of times hitting 52-Week High or All-Time High\n")
        f.write("Higher hits = stronger momentum\n\n")
        f.write(f"Total unique stocks tracked: {len(rows)}\n")
        
        # Stats
        high_momentum = len([r for r in rows if r["Hits"] >= 3])
        medium_momentum = len([r for r in rows if r["Hits"] == 2])
        new_breakouts = len([r for r in rows if r["Hits"] == 1])
        f.write(f"🚀 High momentum (3+ hits): {high_momentum}\n")
        f.write(f"📈 Building momentum (2 hits): {medium_momentum}\n")
        f.write(f"✨ New breakouts (1 hit): {new_breakouts}\n\n")
        
        f.write(table)
        f.write("\n")
    
    return output_file


def update_history(df_highs: pd.DataFrame, date_str: str = None) -> Dict:
    """
    Update the high history with stocks that hit highs today.
    
    Args:
        df_highs: DataFrame with stocks at highs (must have 'Ticker', 'At 52W High', 'At ATH')
        date_str: Date string (YYYY-MM-DD). If None, uses today's date.
    
    Returns:
        Updated history dict
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    history = load_history()
    
    for _, row in df_highs.iterrows():
        ticker = row["Ticker"]
        at_52w = row.get("At 52W High", False)
        at_ath = row.get("At ATH", False)
        
        if not (at_52w or at_ath):
            continue
        
        # Initialize ticker entry if not exists
        if ticker not in history:
            history[ticker] = {
                "count": 0,
                "dates": [],
                "name": row.get("Name", "")
            }
        
        # Check if this date is already recorded
        if date_str not in history[ticker]["dates"]:
            history[ticker]["count"] += 1
            history[ticker]["dates"].append(date_str)
            
            # Keep only last 10 dates (for reference), but we'll show last 2
            history[ticker]["dates"] = history[ticker]["dates"][-10:]
        
        # Update name if available
        if row.get("Name"):
            history[ticker]["name"] = row.get("Name")
    
    save_history(history)
    save_history_readable(history)
    return history


def get_summary(history: Dict = None) -> pd.DataFrame:
    """
    Get a summary DataFrame with hit counts and last 2 dates.
    
    Returns:
        DataFrame with columns: Ticker, Name, Hit Count, Last Date, 2nd Last Date
    """
    if history is None:
        history = load_history()
    
    if not history:
        return pd.DataFrame(columns=["Ticker", "Name", "Hit Count", "Last Date", "2nd Last Date"])
    
    rows = []
    for ticker, data in history.items():
        dates = data.get("dates", [])
        last_date = dates[-1] if len(dates) >= 1 else ""
        second_last = dates[-2] if len(dates) >= 2 else ""
        
        rows.append({
            "Ticker": ticker,
            "Name": data.get("name", ""),
            "Hit Count": data.get("count", 0),
            "Last Date": last_date,
            "2nd Last Date": second_last
        })
    
    df = pd.DataFrame(rows)
    
    # Sort by hit count descending
    df = df.sort_values("Hit Count", ascending=False)
    
    return df


def print_summary():
    """Print the high history summary."""
    df = get_summary()
    
    if df.empty:
        print("No high history recorded yet.")
        return
    
    print("\n" + "=" * 80)
    print("📊 HIGH HISTORY TRACKER - Stocks that hit 52W High or ATH")
    print("=" * 80)
    print(f"\nTotal unique stocks that hit highs: {len(df)}")
    
    # Top 20 most frequent
    print("\n🏆 Top 20 Most Frequent High Hitters:")
    print("-" * 80)
    
    from tabulate import tabulate
    top_20 = df.head(20)
    print(tabulate(top_20, headers="keys", tablefmt="github", showindex=False))
    
    print("\n")


def main():
    """Print the current high history summary."""
    print_summary()


if __name__ == "__main__":
    main()
