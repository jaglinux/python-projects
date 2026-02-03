#!/usr/bin/env python3

import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

HISTORY_FILE = "stock_history.txt"
RECOMMENDATIONS_FILE = "recommendations.md"


def load_latest_snapshot() -> pd.DataFrame:
    """Load stock_history.txt and return only the latest timestamp's data."""
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame()

    df = pd.read_csv(HISTORY_FILE, parse_dates=["timestamp"])
    if df.empty:
        return pd.DataFrame()

    latest_time = df["timestamp"].max()
    df_latest = df[df["timestamp"] == latest_time].copy()
    return df_latest


def load_recommendation_history(path: str = RECOMMENDATIONS_FILE) -> str:
    """
    Load existing recommendations.md as plain text (without the heading),
    so the LLM can see what was recommended before.
    """
    p = Path(path)
    if not p.exists():
        return ""

    text = p.read_text(encoding="utf-8")

    # Strip the top-level heading if present to keep it cleaner
    lines = text.splitlines()
    if lines and lines[0].lstrip().startswith("#"):
        lines = lines[1:]
    return "\n".join(lines).strip()


def generate_recommendation(df_latest: pd.DataFrame) -> str:
    """
    Use LangChain + GPT to analyze the latest stock data and generate
    buy recommendations based on sentiment, market cap, price changes, etc.
    The model is free to recommend any number of stocks and use its own style.
    """
    if df_latest.empty:
        return "No data available for analysis."

    # Latest snapshot as markdown table
    table_md = df_latest.to_markdown(index=False)

    # Load prior recommendation history (optional context)
    history_text = load_recommendation_history()

    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert stock analyst.

You are given:
1) A table with today's data for a small set of stocks.
2) A history of past daily recommendations (if any).

Your task:
- Recommend any number of BUY ideas you think make sense today (including zero, if nothing is attractive).
- Focus especially on:
  - Positive sentiment.
  - Lower market cap (more upside potential).
  - Strong recent momentum in daily/weekly % changes when available.
- You do NOT need to consider the 52-week high distance as a constraint.
  - Even if a stock is far below its 52-week high, it can still be a good BUY if sentiment and other factors are strong.

Style:
- You are free to choose your own clear, concise style.
- Always include the current price in parentheses next to each ticker symbol, e.g. KVYO ($25.62).
- Keep the whole answer under about 120 words.
- It is okay to recommend only one stock or even none if you think nothing meets the bar.""",
            ),
            (
                "human",
                """Here is today's stock data:

{table}

Here is the history of previous daily recommendations (most recent first, may be empty):

{history}

Please provide today's BUY recommendation(s) now.""",
            ),
        ]
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    chain = prompt_template | llm
    response = chain.invoke(
        {
            "table": table_md,
            "history": history_text or "No prior recommendations available.",
        }
    )

    return response.content.strip()


def append_recommendation_md(
    recommendation_text: str, path: str = RECOMMENDATIONS_FILE
):
    """
    Prepend a timestamped recommendation so newest is at the top (after header).
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    p = Path(path)

    new_line = f"- {now} — {recommendation_text}\n"

    if not p.exists():
        p.write_text("# Daily Stock Recommendations\n\n" + new_line, encoding="utf-8")
        return

    existing = p.read_text(encoding="utf-8")
    lines = existing.splitlines(keepends=True)

    if not lines:
        p.write_text("# Daily Stock Recommendations\n\n" + new_line, encoding="utf-8")
        return

    header = lines[0]
    rest = lines[1:]

    if rest and rest[0].strip() != "":
        rest = ["\n"] + rest

    new_content = header + "\n" + new_line + "".join(rest[1:])
    p.write_text(new_content, encoding="utf-8")


def main():
    print("\n=== Generating AI Recommendation ===")

    df_latest = load_latest_snapshot()
    if df_latest.empty:
        print("No recent data to analyze.")
        return

    recommendation = generate_recommendation(df_latest)

    print(f"\n📊 Recommendation:\n{recommendation}\n")

    append_recommendation_md(recommendation)
    print(f"Saved to {RECOMMENDATIONS_FILE}")


if __name__ == "__main__":
    main()
