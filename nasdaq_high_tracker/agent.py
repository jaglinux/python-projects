#!/usr/bin/env python3
"""
AI Agent module for NASDAQ High Tracker.
Uses LangChain + GPT as a momentum analyst to recommend stocks based on high frequency.
"""

import os
from datetime import datetime, timezone
from tabulate import tabulate

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import high_history


# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")


def create_stocks_table(df: pd.DataFrame, history: dict = None) -> tuple:
    """
    Create a formatted table of stocks at highs with momentum data.
    Returns: (table_string, summary_dict)
    """
    if df.empty:
        return "No stocks at highs.", {"total": 0, "ath": 0, "52w_only": 0}
    
    # Load history if not provided
    if history is None:
        history = high_history.load_history()
    
    # Count stocks at ATH and 52W high
    at_ath = len(df[df["At ATH"] == True]) if "At ATH" in df.columns else 0
    at_52w = len(df[df["At 52W High"] == True]) if "At 52W High" in df.columns else 0
    at_52w_only = at_52w - at_ath  # 52W high but not ATH
    
    summary = {
        "total": len(df),
        "ath": at_ath,
        "52w_only": at_52w_only
    }
    
    # Add momentum columns from history
    df = df.copy()
    df["Hits"] = df["Ticker"].apply(lambda t: history.get(t, {}).get("count", 1))
    df["Last Hit"] = df["Ticker"].apply(
        lambda t: history.get(t, {}).get("dates", [])[-1] if history.get(t, {}).get("dates") else "Today"
    )
    df["2nd Last"] = df["Ticker"].apply(
        lambda t: history.get(t, {}).get("dates", [])[-2] if len(history.get(t, {}).get("dates", [])) >= 2 else ""
    )
    
    # Select columns for display (include momentum columns)
    display_cols = ["Ticker", "Name", "Price", "Market Cap (B)", "Hits", "Last Hit", "2nd Last",
                    "Sentiment", "% From 52W High", "% From ATH"]
    
    # Filter to only columns that exist
    available_cols = [c for c in display_cols if c in df.columns]
    df_display = df[available_cols].copy()
    
    # Sort by Hits (momentum) descending, then by % From 52W High
    df_display = df_display.sort_values(["Hits", "% From 52W High"], ascending=[False, False])
    
    # Reset index and add row number
    df_display = df_display.reset_index(drop=True)
    df_display.index = df_display.index + 1  # Start from 1
    df_display.index.name = "#"
    
    # Format the table with row numbers
    table = tabulate(
        df_display,
        headers="keys",
        tablefmt="github",
        showindex=True,
        floatfmt=".2f",
    )
    
    return table, summary


def generate_recommendations(table_md: str, history: dict = None) -> str:
    """
    Use GPT as a momentum analyst to generate recommendations.
    Momentum = how many times a stock hits highs. More hits = stronger momentum.
    """
    # Get top momentum stocks for context
    momentum_context = ""
    if history:
        sorted_history = sorted(history.items(), key=lambda x: x[1].get("count", 0), reverse=True)
        top_momentum = sorted_history[:10]
        if top_momentum:
            momentum_lines = [f"- {t}: {d['count']} hits (last: {d['dates'][-1] if d.get('dates') else 'N/A'})" 
                             for t, d in top_momentum]
            momentum_context = "\n\nTop 10 Momentum Leaders (all-time high hit frequency):\n" + "\n".join(momentum_lines)
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are a STOCK MOMENTUM ANALYST. Your job is to identify and recommend stocks with the strongest momentum.

MOMENTUM DEFINITION:
- Momentum = how frequently a stock hits 52-week high or all-time high
- The "Hits" column shows how many times each stock has hit highs (tracked over time)
- MORE HITS = STRONGER MOMENTUM = stock is consistently making new highs
- Stocks hitting highs repeatedly are showing sustained buying pressure and institutional interest

MOMENTUM ANALYSIS:
- High hit count (3+) = Strong momentum, proven winner, institutions are accumulating
- Medium hit count (2) = Building momentum, worth watching
- First time hit (1) = New breakout, could be start of momentum or one-off

## 🚀 MOMENTUM PICKS - TOP RECOMMENDATIONS
Pick stocks with the STRONGEST MOMENTUM based on:
1. Higher "Hits" count is the PRIMARY factor (more hits = more momentum)
2. Recent hits (check Last Hit / 2nd Last dates) indicate active momentum
3. Bullish sentiment confirms the momentum
4. Larger market cap provides stability

For each pick: **TICKER** ($Price) - Hits: X - Brief reason focusing on momentum strength.

## 🤖 TECH MOMENTUM PICKS
Pick tech/AI stocks with strong momentum from:
- Technology, software, cloud, semiconductors
- AI and machine learning companies

For each pick: **TICKER** ($Price) - Hits: X - Brief reason.
Skip this section if no qualifying tech stocks."""),
        ("human", """Here are today's S&P 500 stocks at 52-week high or all-time high with their momentum data:

{table}
{momentum_context}

Analyze the momentum and provide your recommendations:""")
    ])
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt_template | llm
    
    response = chain.invoke({"table": table_md, "momentum_context": momentum_context})
    return response.content.strip()


def save_analysis_md(table: str, summary: dict, recommendations: str):
    """Save table and recommendations to markdown file, prepending new entries at the top."""
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")
    
    filepath = os.path.join(OUTPUT_DIR, "ai_analysis.md")
    
    new_entry = f"""---
## {timestamp}

### 📊 Stocks at Highs (with Momentum Data)

**Total: {summary['total']} stocks** | 🏆 At ATH: {summary['ath']} | 🔥 At 52W High only: {summary['52w_only']}

> **Hits** = Number of times the stock has hit 52W High or ATH (higher = stronger momentum)

{table}

### 🚀 AI Momentum Analysis

{recommendations}

"""
    
    # Read existing content if file exists
    existing_content = ""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            existing_content = f.read()
    
    # Prepend new entry (newest at top)
    header = "# S&P 500 Momentum Tracker - AI Analysis\n\n"
    if existing_content.startswith(header):
        existing_content = existing_content[len(header):]
    
    # Also handle old header format
    old_header = "# S&P 500 High Tracker - AI Analysis\n\n"
    if existing_content.startswith(old_header):
        existing_content = existing_content[len(old_header):]
    
    content = header + new_entry + existing_content
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath


def main(df_stocks: pd.DataFrame = None):
    """
    Main function to generate AI momentum analysis.
    
    Args:
        df_stocks: DataFrame with stocks at highs (required)
    """
    print("\n=== Generating AI Momentum Analysis ===")
    
    if df_stocks is None or df_stocks.empty:
        print("No data to analyze.")
        return
    
    # Load high history for momentum data
    history = high_history.load_history()
    print(f"Loaded momentum history for {len(history)} stocks")
    
    # Create stocks table with momentum data
    print("Creating stocks table with momentum data...")
    table, summary = create_stocks_table(df_stocks, history)
    print(f"\n🏆 At ATH: {summary['ath']} | 🔥 At 52W High only: {summary['52w_only']} | Total: {summary['total']}")
    print(f"\n{table}\n")
    
    # Generate AI momentum recommendations
    print("Generating AI momentum recommendations...")
    recommendations = generate_recommendations(table, history)
    print(f"\n{recommendations}\n")
    
    # Save to file (table first, then recommendations)
    filepath = save_analysis_md(table, summary, recommendations)
    print(f"Analysis saved to {filepath}")
