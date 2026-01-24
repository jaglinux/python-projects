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

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
HISTORY_FILE = os.path.join(OUTPUT_DIR, "stocks_at_highs.txt")


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
        ("system", """You are an expert technical analyst. The data provided contains S&P 500 stocks at 52-Week High or All-Time High.

List ALL stocks in priority order:

## 🏆 AT ALL-TIME HIGH (Highest Priority)
(Stocks where At ATH = True)
These are the strongest stocks - making new all-time highs.

## 🔥 AT 52-WEEK HIGH ONLY
(Stocks where At 52W High = True but At ATH = False)
These stocks are at 52-week highs but were higher at some point in the past.

For each stock show: Ticker, Name, Price, % from high, Sentiment
Within each section, group by sentiment: Bullish first, then Neutral, then Bearish.

Include ALL stocks from the data provided.

## 💡 AI INSIGHTS - TOP Stock PICKS
From the stocks listed above, pick up to 3-5 top stocks (if available) based on:
- Bullish sentiment preferred
- Stocks at ATH have priority over 52W high only
- Strong momentum indicators

For each recommendation, briefly explain why (1 sentence). Skip if none qualify.

## 💡 AI INSIGHTS - TECH & AI Stock PICKS
From the stocks listed above, pick up to 3-5 (if available) that are in these sectors:
- Technology companies (software, hardware, cloud)
- AI and machine learning companies
- Semiconductors and chip makers
- New-age digital/tech companies

Only pick from the ATH or 52W high stocks listed above. Skip this section if no tech stocks are at highs."""),
        ("human", """S&P 500 stocks at highs:

{at_highs_summary}

### Data:
{momentum_table}
{breakouts_section}

Provide the complete list in priority order:""")
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


def save_analysis_md(analysis_text: str):
    """Save analysis to markdown file, prepending new entries at the top."""
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")
    
    filepath = os.path.join(OUTPUT_DIR, "ai_analysis.md")
    
    new_entry = f"""---
## {timestamp}

{analysis_text}

"""
    
    # Read existing content if file exists
    existing_content = ""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            existing_content = f.read()
    
    # Prepend new entry (newest at top)
    header = "# S&P 500 High Tracker - AI Analysis\n\n"
    if existing_content.startswith(header):
        existing_content = existing_content[len(header):]
    
    content = header + new_entry + existing_content
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath


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
    
    # Save to new file with date
    filepath = save_analysis_md(analysis)
    print(f"Analysis saved to {filepath}")


if __name__ == "__main__":
    main()
