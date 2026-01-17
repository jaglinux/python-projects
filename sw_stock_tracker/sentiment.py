#!/usr/bin/env python3

import pandas as pd
import yfinance as yf
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from snapshot import TICKERS  # import from snapshot.py

# Download VADER lexicon if not present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)


def fetch_sentiment_for_ticker(ticker: str, max_headlines: int = 5) -> tuple:
    """
    Fetch recent news headlines for a ticker using yfinance and compute
    average VADER compound sentiment score.
    Returns (sentiment_label, headlines_list).
    sentiment_label: "Positive", "Negative", or "Neutral"
    headlines_list: list of headline strings
    """
    try:
        t = yf.Ticker(ticker)
        news = t.news
        
        if not news:
            return "Neutral", []
        
        sia = SentimentIntensityAnalyzer()
        scores = []
        headlines = []
        
        for item in news[:max_headlines]:
            # Title is nested in item["content"]["title"]
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
            return "Neutral", headlines
        
        avg_score = sum(scores) / len(scores)
        
        # Classify based on compound score thresholds
        if avg_score >= 0.05:
            label = "Positive"
        elif avg_score <= -0.05:
            label = "Negative"
        else:
            label = "Neutral"
        
        return label, headlines
    
    except Exception as e:
        print(f"Warning: failed to get sentiment for {ticker}: {e}")
        return "Neutral", []


def fetch_sentiment(tickers: list) -> tuple:
    """
    Fetch sentiment scores for a list of tickers.
    Returns (DataFrame, news_dict).
    DataFrame: columns Ticker, Sentiment
    news_dict: {ticker: [headlines]}
    """
    results = []
    news_dict = {}
    
    for ticker in tickers:
        label, headlines = fetch_sentiment_for_ticker(ticker)
        results.append({"Ticker": ticker, "Sentiment": label})
        news_dict[ticker] = headlines
    
    return pd.DataFrame(results), news_dict


def create_news_image(news_dict: dict, filename: str = "news_summary.png"):
    """
    Create a WhatsApp-shareable image with news headlines per ticker.
    """
    fig, ax = plt.subplots(figsize=(12, len(TICKERS) * 1.2))
    ax.axis('off')
    
    y_pos = 0.98
    line_height = 1.0 / (len(TICKERS) + 2)
    
    # Title
    ax.text(0.5, y_pos, "📰 Stock News Summary", 
            fontsize=16, weight='bold', ha='center', va='top',
            transform=ax.transAxes)
    y_pos -= line_height * 1.5
    
    for ticker in TICKERS:
        headlines = news_dict.get(ticker, [])
        
        # Ticker name
        ax.text(0.02, y_pos, f"{ticker}:", 
                fontsize=11, weight='bold', va='top',
                transform=ax.transAxes)
        y_pos -= line_height * 0.6
        
        if headlines:
            # Show first 2 headlines to keep image compact
            for i, headline in enumerate(headlines[:2]):
                # Truncate long headlines
                if len(headline) > 80:
                    headline = headline[:77] + "..."
                ax.text(0.05, y_pos, f"• {headline}", 
                        fontsize=8, va='top', wrap=True,
                        transform=ax.transAxes)
                y_pos -= line_height * 0.5
        else:
            ax.text(0.05, y_pos, "• No recent news", 
                    fontsize=8, style='italic', va='top',
                    transform=ax.transAxes)
            y_pos -= line_height * 0.5
        
        y_pos -= line_height * 0.3  # spacing between tickers
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved {filename} – share this image on WhatsApp.")


def main() -> pd.DataFrame:
    print("Fetching sentiment scores (VADER)...")
    df, news_dict = fetch_sentiment(TICKERS)
    print(df)
    
    # Create shareable news image
    create_news_image(news_dict)
    
    return df


if __name__ == "__main__":
    main()
