# tracker.py
import os
from datetime import datetime, timezone
import pandas as pd
import snapshot  # imports snapshot.py in same directory

HISTORY_CSV = "stock_history.csv"

def load_history():
    if os.path.exists(HISTORY_CSV):
        return pd.read_csv(HISTORY_CSV, parse_dates=["timestamp"])
    else:
        return pd.DataFrame(columns=["timestamp", "Ticker", "Price", "Market Cap (B)"])

def save_history(df_hist: pd.DataFrame):
    df_hist.to_csv(HISTORY_CSV, index=False)

def add_today_snapshot(df_hist: pd.DataFrame, df_snap: pd.DataFrame) -> pd.DataFrame:
    now = datetime.now(timezone.utc)
    df_snap = df_snap.copy()
    df_snap["timestamp"] = now

    # align columns
    df_snap = df_snap[["timestamp", "Ticker", "Price", "Market Cap (B)"]]

    return pd.concat([df_hist, df_snap], ignore_index=True)

def compute_changes(df_hist: pd.DataFrame):
    # Sort for pct_change
    df_hist = df_hist.sort_values(["Ticker", "timestamp"])

    # For each ticker, compute daily and weekly change from last observations
    # Here, "daily" = last vs previous row per ticker
    #       "weekly" = last vs row 5 steps back per ticker (approx 5 trading days)
    results = []
    for ticker, g in df_hist.groupby("Ticker"):
        g = g.reset_index(drop=True)
        if len(g) == 0:
            continue

        last_row = g.iloc[-1]

        # daily change
        if len(g) >= 2 and g["Price"].iloc[-2] not in (None, 0) and g["Price"].iloc[-1] not in (None, 0):
            daily_change = (g["Price"].iloc[-1] / g["Price"].iloc[-2] - 1) * 100
        else:
            daily_change = None

        # weekly change (5 entries ago)
        if len(g) >= 6 and g["Price"].iloc[-6] not in (None, 0) and g["Price"].iloc[-1] not in (None, 0):
            weekly_change = (g["Price"].iloc[-1] / g["Price"].iloc[-6] - 1) * 100
        else:
            weekly_change = None

        results.append(
            {
                "Ticker": ticker,
                "Latest Price": last_row["Price"],
                "Market Cap (B)": last_row["Market Cap (B)"],
                "Daily Change %": daily_change,
                "Weekly Change %": weekly_change,
            }
        )

    return pd.DataFrame(results)

def main():
    # 1) get latest snapshot from first script
    df_snap = snapshot.main()  # calls main() in snapshot.py[web:114]

    # 2) load and update history
    df_hist = load_history()
    df_hist = add_today_snapshot(df_hist, df_snap)
    save_history(df_hist)

    # 3) compute changes
    df_changes = compute_changes(df_hist)

    # 4) pretty print
    with pd.option_context("display.float_format", "{:.2f}".format):
        print("\n=== Daily & Weekly Changes ===")
        print(df_changes)

if __name__ == "__main__":
    main()
