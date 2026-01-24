#!/usr/bin/env python3
"""
Sentiment module for NASDAQ High Tracker.
Fetches news headlines and computes VADER sentiment scores.
"""

import pandas as pd
import yfinance as yf
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

from snapshot import TICKERS

# Download VADER lexicon if not present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)


def fetch_sentiment_for_ticker(ticker: str, max_headlines: int = 5) -> tuple:
    """
    Fetch recent news headlines for a ticker using yfinance and compute
    average VADER compound sentiment score.
    
    Returns:
        (sentiment_label, compound_score, headlines_list)
        - sentiment_label: "Bullish", "Bearish", or "Neutral"
        - compound_score: float average VADER compound score
        - headlines_list: list of headline strings
    """
    try:
        t = yf.Ticker(ticker)
        news = t.news
        
        if not news:
            return "Neutral", 0.0, []
        
        sia = SentimentIntensityAnalyzer()
        scores = []
        headlines = []
        
        for item in news[:max_headlines]:
            title = None
            if isinstance(item, dict):
                content = item.get("content", {})
                if isinstance(content, dict):
                    title = content.get("title")
            
            if title and isinstance(title, str):
                sentiment = sia.polarity_scores(title)
                scores.append(sentiment["compound"])
                headlines.append(title)
        
        if not scores:
            return "Neutral", 0.0, headlines
        
        avg_score = sum(scores) / len(scores)
        
        # Classify with market-friendly labels
        if avg_score >= 0.1:
            label = "Bullish"
        elif avg_score <= -0.1:
            label = "Bearish"
        else:
            label = "Neutral"
        
        return label, avg_score, headlines
    
    except Exception as e:
        print(f"Warning: failed to get sentiment for {ticker}: {e}")
        return "Neutral", 0.0, []


def fetch_sentiment(tickers: list) -> tuple:
    """
    Fetch sentiment scores for a list of tickers.
    
    Returns:
        (DataFrame, news_dict)
        - DataFrame: columns Ticker, Sentiment, Sentiment Score
        - news_dict: {ticker: [headlines]}
    """
    results = []
    news_dict = {}
    
    for ticker in tickers:
        label, score, headlines = fetch_sentiment_for_ticker(ticker)
        results.append({
            "Ticker": ticker, 
            "Sentiment": label,
            "Sentiment Score": score
        })
        news_dict[ticker] = headlines
    
    return pd.DataFrame(results), news_dict


def create_news_image(news_dict: dict, filename: str = "news_summary.png"):
    """
    Create a shareable image with news headlines per ticker.
    Highlights tickers with bullish sentiment for breakout potential.
    """
    fig, ax = plt.subplots(figsize=(14, len(TICKERS) * 0.9 + 2))
    ax.axis('off')
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    
    y_pos = 0.97
    line_height = 1.0 / (len(TICKERS) + 3)
    
    # Title
    ax.text(0.5, y_pos, "📈 NASDAQ High Tracker - News Summary", 
            fontsize=18, weight='bold', ha='center', va='top',
            color='#00d4ff', transform=ax.transAxes)
    y_pos -= line_height * 1.8
    
    sia = SentimentIntensityAnalyzer()
    
    for ticker in TICKERS:
        headlines = news_dict.get(ticker, [])
        
        # Calculate sentiment for color coding
        if headlines:
            scores = [sia.polarity_scores(h)["compound"] for h in headlines[:3]]
            avg_score = sum(scores) / len(scores) if scores else 0
            if avg_score >= 0.1:
                ticker_color = '#00ff88'  # Green for bullish
            elif avg_score <= -0.1:
                ticker_color = '#ff4444'  # Red for bearish
            else:
                ticker_color = '#ffffff'  # White for neutral
        else:
            ticker_color = '#888888'
        
        # Ticker name
        ax.text(0.02, y_pos, f"{ticker}", 
                fontsize=12, weight='bold', va='top',
                color=ticker_color, transform=ax.transAxes)
        
        # Headlines
        if headlines:
            headline_text = headlines[0][:90] + "..." if len(headlines[0]) > 90 else headlines[0]
            ax.text(0.10, y_pos, f"• {headline_text}", 
                    fontsize=9, va='top', color='#cccccc',
                    transform=ax.transAxes)
        else:
            ax.text(0.10, y_pos, "• No recent news", 
                    fontsize=9, style='italic', va='top', color='#666666',
                    transform=ax.transAxes)
        
        y_pos -= line_height
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', 
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    print(f"Saved {filename}")


def main(tickers: list = None) -> pd.DataFrame:
    """
    Main function to fetch sentiment for specified tickers.
    
    Args:
        tickers: List of ticker symbols. If None, uses all TICKERS from snapshot.
    """
    if tickers is None:
        tickers = TICKERS
    
    if not tickers:
        print("No tickers to fetch sentiment for.")
        return pd.DataFrame(columns=["Ticker", "Sentiment", "Sentiment Score"])
    
    print(f"Fetching sentiment scores for {len(tickers)} stocks...")
    df, news_dict = fetch_sentiment(tickers)
    
    # Sort by sentiment score descending
    df = df.sort_values("Sentiment Score", ascending=False)
    print(df.to_string(index=False))
    
    return df


if __name__ == "__main__":
    # When run standalone, fetch for all tickers
    main()
