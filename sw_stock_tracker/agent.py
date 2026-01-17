#!/usr/bin/env python3

import os
from datetime import datetime, timezone
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

HISTORY_FILE = "stock_history.txt"
RECOMMENDATIONS_FILE = "recommendations.md"

def load_latest_snapshot() -> pd.DataFrame:
    """
    Load stock_history.txt and return only the latest timestamp's data.
    """
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame()
    
    df = pd.read_csv(HISTORY_FILE, parse_dates=["timestamp"])
    
    if df.empty:
        return pd.DataFrame()
    
    # Get latest timestamp
    latest_time = df["timestamp"].max()
    
    # Filter to latest snapshot only
    df_latest = df[df["timestamp"] == latest_time].copy()
    
    return df_latest


def generate_recommendation(df_latest: pd.DataFrame) -> str:
    """
    Use LangChain + GPT to analyze the latest stock data and generate
    buy recommendations based on sentiment, market cap, price changes, etc.
    Returns a concise recommendation string.
    """
    if df_latest.empty:
        return "No data available for analysis."
    
    # Convert DataFrame to a clean markdown table for the LLM
    table_md = df_latest.to_markdown(index=False)
    
    # Create prompt
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are an expert stock analyst. Analyze the provided stock data and identify 2-3 BUY opportunities based on:
- Positive sentiment
- Low market cap (higher growth potential)
- Strong daily/weekly momentum (positive % changes)
- Not too far from 52-week high (reasonable entry point)

Be concise and actionable. Format: "Buy TICKER1, TICKER2 because [brief reason]." Keep under 100 words."""),
        ("human", "Here is today's stock data:\n\n{table}")
    ])
    
    # Initialize LLM (GPT-4 or GPT-3.5-turbo)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Create chain
    chain = prompt_template | llm
    
    # Run
    response = chain.invoke({"table": table_md})
    
    return response.content.strip()


def append_recommendation_md(recommendation_text: str, path: str = RECOMMENDATIONS_FILE):
    """
    Append a timestamped recommendation to recommendations.md
    """
    from pathlib import Path
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    p = Path(path)

    if not p.exists():
        p.write_text("# Daily Stock Recommendations\n\n", encoding="utf-8")

    line = f"- {now} — {recommendation_text}\n"
    with p.open("a", encoding="utf-8") as f:
        f.write(line)


def main():
    print("\n=== Generating AI Recommendation ===")
    
    df_latest = load_latest_snapshot()
    
    if df_latest.empty:
        print("No recent data to analyze.")
        return
    
    recommendation = generate_recommendation(df_latest)
    
    print(f"\n📊 Recommendation:\n{recommendation}\n")
    
    # Append to markdown log
    append_recommendation_md(recommendation)
    print(f"Saved to {RECOMMENDATIONS_FILE}")


if __name__ == "__main__":
    main()
