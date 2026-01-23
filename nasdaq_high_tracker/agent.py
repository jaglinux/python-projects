#!/usr/bin/env python3
"""
AI Agent module for NASDAQ High Tracker.
Uses LangChain + GPT to analyze high breakouts and generate trading insights.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

HISTORY_FILE = "high_tracker_history.csv"
ANALYSIS_FILE = "high_analysis.md"


def load_latest_snapshot() -> pd.DataFrame:
    """Load the latest snapshot from history file."""
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame()
    
    df = pd.read_csv(HISTORY_FILE, parse_dates=["timestamp"])
    
    if df.empty:
        return pd.DataFrame()
    
    latest_time = df["timestamp"].max()
    df_latest = df[df["timestamp"] == latest_time].copy()
    
    return df_latest


def generate_high_analysis(df_momentum: pd.DataFrame, df_breakouts: pd.DataFrame) -> str:
    """
    Use LangChain + GPT to analyze stocks at/near highs and identify opportunities.
    
    Args:
        df_momentum: DataFrame with momentum and high proximity data
        df_breakouts: DataFrame of stocks that just broke to new highs
    
    Returns:
        Analysis string with trading insights
    """
    if df_momentum.empty:
        return "No data available for analysis."
    
    # Prepare data summaries for the LLM
    momentum_md = df_momentum.to_markdown(index=False)
    
    breakouts_md = ""
    if not df_breakouts.empty:
        breakouts_md = f"\n\n### New Breakouts:\n{df_breakouts.to_markdown(index=False)}"
    
    # Stocks at highs
    at_52w = df_momentum[df_momentum["At 52W High"] == True]
    at_ath = df_momentum[df_momentum["At ATH"] == True]
    
    at_highs_summary = f"""
### Stocks at 52-Week High: {len(at_52w)} stocks
### Stocks at All-Time High: {len(at_ath)} stocks
"""
    
    # Create prompt for high-focused analysis
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are an expert technical analyst specializing in breakout trading and momentum strategies.

Analyze the provided NASDAQ stock data focusing on:
1. **Stocks at 52-Week Highs** - These show strong momentum; identify the best ones to buy on continuation
2. **Stocks at All-Time Highs** - Ultimate strength; look for low-risk entries on pullbacks
3. **Approaching Highs** - Stocks within 5% of 52W high with bullish sentiment = potential breakout candidates
4. **Momentum Leaders** - Positive "High Momentum" means they're moving toward highs

Your analysis should:
- Identify 2-3 TOP PICKS for breakout trading (stocks at or near highs with bullish sentiment)
- Identify 1-2 WATCH LIST stocks approaching highs
- Provide brief reasoning based on the data (momentum, sentiment, distance from high)
- Include current price for each recommendation

Format your response in clear sections:
## 🎯 TOP PICKS (Buy Now)
## 👀 WATCH LIST (Approaching Breakout)
## ⚠️ CAUTION (Overbought/Risky)

Keep analysis under 200 words. Be specific with prices and percentages."""),
        ("human", """Here is today's NASDAQ high tracker data:

{at_highs_summary}

### Full Momentum Data:
{momentum_table}
{breakouts_section}

Provide your breakout trading analysis:""")
    ])
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    
    # Create chain and run
    chain = prompt_template | llm
    
    response = chain.invoke({
        "at_highs_summary": at_highs_summary,
        "momentum_table": momentum_md,
        "breakouts_section": breakouts_md
    })
    
    return response.content.strip()


def append_analysis_md(analysis_text: str, path: str = ANALYSIS_FILE):
    """Append timestamped analysis to the markdown log."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    p = Path(path)

    if not p.exists():
        p.write_text("# NASDAQ High Tracker - AI Analysis Log\n\n", encoding="utf-8")

    entry = f"""
---
### {now}

{analysis_text}

"""
    with p.open("a", encoding="utf-8") as f:
        f.write(entry)


def main(df_momentum: pd.DataFrame = None, df_breakouts: pd.DataFrame = None):
    """
    Main function to generate AI analysis.
    
    Args:
        df_momentum: Pre-computed momentum DataFrame (optional)
        df_breakouts: Pre-computed breakouts DataFrame (optional)
    """
    print("\n=== Generating AI High Analysis ===")
    
    # If no data provided, load from history
    if df_momentum is None:
        df_latest = load_latest_snapshot()
        if df_latest.empty:
            print("No recent data to analyze.")
            return
        df_momentum = df_latest
        df_breakouts = pd.DataFrame()
    
    if df_breakouts is None:
        df_breakouts = pd.DataFrame()
    
    # Generate analysis
    analysis = generate_high_analysis(df_momentum, df_breakouts)
    
    print(f"\n{analysis}\n")
    
    # Append to log
    append_analysis_md(analysis)
    print(f"Analysis saved to {ANALYSIS_FILE}")


if __name__ == "__main__":
    main()
