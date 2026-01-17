#!/usr/bin/env python3

import os
from datetime import datetime, timezone, timedelta

import pandas as pd

import snapshot  # same directory

HISTORY_FILE = "stock_history.txt"  # CSV-format text


def load_history() -> pd.DataFrame:
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE, parse_dates=["timestamp"])
    else:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "Ticker",
                "Price",
                "Market Cap (B)",
                "52W High",
                "% From 52W High",
            ]
        )


def save_history(df_hist: pd.DataFrame):
    df_hist.to_csv(HISTORY_FILE, index=False)


def latest_prices_by_ticker(df_hist: pd.DataFrame) -> pd.Series:
    if df_hist.empty:
        return pd.Series(dtype=float)
    df_sorted = df_hist.sort_values(["Ticker", "timestamp"])
    return df_sorted.groupby("Ticker")["Price"].last()


def prices_changed(df_snap: pd.DataFrame, last_prices: pd.Series) -> bool:
    if last_prices.empty:
        # first ever run -> treat as "changed" so we create baseline
        return True

    for _, row in df_snap.iterrows():
        ticker = row["Ticker"]
        new_price = row["Price"]
        old_price = last_prices.get(ticker, None)

        # skip if new_price is missing
        if pd.isna(new_price):
            continue

        # if old_price missing -> changed
        if old_price is None or pd.isna(old_price):
            return True

        # compare as floats with small tolerance to avoid float precision issues
        try:
            if abs(float(new_price) - float(old_price)) > 0.01:  # tolerance for rounding
                return True
        except Exception:
            return True

    return False

def compute_changes(df_hist: pd.DataFrame) -> pd.DataFrame:
    df_hist = df_hist.sort_values(["Ticker", "timestamp"])

    results = []
    for ticker, g in df_hist.groupby("Ticker"):
        g = g.reset_index(drop=True)
        if len(g) == 0:
            continue

        last_row = g.iloc[-1]
        last_time = last_row["timestamp"]
        last_price = last_row["Price"]

        # daily
        if (
            len(g) >= 2
            and pd.notna(g["Price"].iloc[-2])
            and pd.notna(last_price)
            and g["Price"].iloc[-2] not in (None, 0)
            and last_price not in (None, 0)
        ):
            prev_price = g["Price"].iloc[-2]
            daily_change = (last_price / prev_price - 1) * 100
        else:
            daily_change = None

        # weekly: last vs most recent row at least 5 days earlier
        cutoff_time = last_time - timedelta(days=5)
        weekly_candidates = g[g["timestamp"] <= cutoff_time]

        if (
            not weekly_candidates.empty
            and pd.notna(last_price)
            and last_price not in (None, 0)
        ):
            weekly_row = weekly_candidates.iloc[-1]
            weekly_price = weekly_row["Price"]
            if pd.notna(weekly_price) and weekly_price not in (None, 0):
                weekly_change = (last_price / weekly_price - 1) * 100
            else:
                weekly_change = None
        else:
            weekly_change = None

        results.append(
            {
                "Ticker": ticker,
                "Latest Price": last_price,
                "Market Cap (B)": last_row.get("Market Cap (B)"),
                "Daily Change %": daily_change,
                "Weekly Change %": weekly_change,
                "% From 52W High": last_row.get("% From 52W High"),
            }
        )

    return pd.DataFrame(results)


def main():
    # fresh snapshot only (no history writes here)
    df_snap = snapshot.main()

    df_hist_before = load_history()
    last_prices = latest_prices_by_ticker(df_hist_before)

    if not prices_changed(df_snap, last_prices):
        print("\nNo price changes vs last stored snapshot; not appending or recomputing.")
        return

    # append new snapshot
    now = datetime.now(timezone.utc)
    df_append = df_snap.copy()
    df_append["timestamp"] = now

    for col in ["Ticker", "Price", "Market Cap (B)", "52W High", "% From 52W High"]:
        if col not in df_append.columns:
            df_append[col] = pd.NA

    cols = ["timestamp", "Ticker", "Price", "Market Cap (B)", "52W High", "% From 52W High"]
    df_append = df_append[cols]

    df_hist_after = pd.concat([df_hist_before, df_append], ignore_index=True)
    save_history(df_hist_after)

    # compute changes
    df_changes = compute_changes(df_hist_after)
    with pd.option_context("display.float_format", "{:.2f}".format):
        print("\n=== Daily & Weekly Changes ===")
        print(df_changes.sort_values("Ticker"))


if __name__ == "__main__":
    main()
