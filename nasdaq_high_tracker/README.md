# S&P 500 High Tracker

A Python toolkit for tracking 52-week highs and all-time highs for S&P 500 stocks. Generates AI-powered analysis and recommendations.

## Features

- **S&P 500 Coverage** - Track all 500 stocks in the S&P 500 index
- **52-Week High Tracking** - Monitor stocks at their 52-week highs
- **All-Time High Detection** - Identify stocks making new all-time highs
- **Sentiment Analysis** - VADER-based news sentiment (only for stocks at highs)
- **AI Analysis** - GPT-powered stock lists and recommendations

## Project Structure

```
nasdaq_high_tracker/
├── fetch_tickers.py    # Fetches S&P 500 tickers from Wikipedia
├── ticker.txt          # List of tickers (generated)
├── snapshot.py         # Fetches price, 52W high, ATH data
├── sentiment.py        # News sentiment analysis
├── tracker.py          # Main orchestrator
├── agent.py            # AI analysis (LangChain + GPT)
├── requirements.txt    # Python dependencies
└── output/             # All output files
    ├── snapshot.txt           # Current snapshot data
    ├── stocks_at_highs.txt    # History of stocks at highs
    └── ai_analysis.md         # AI analysis (newest at top)
```

## Installation

```bash
cd nasdaq_high_tracker
pip install -r requirements.txt
python -c "import nltk; nltk.download('vader_lexicon')"
```

## Configuration

Set your OpenAI API key:

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "your-api-key-here"
```

```bash
# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Step 1: Fetch S&P 500 Tickers

```bash
python fetch_tickers.py
```

Creates `ticker.txt` with ~500 S&P 500 tickers.

### Step 2: Run the Tracker

```bash
# Full run - fetches live data from yfinance
python tracker.py

# Cache mode - uses saved snapshot (no API calls, for testing)
python tracker.py --use-cache
python tracker.py -c
```

### What it does:

1. Fetches prices and high data for all S&P 500 stocks
2. Identifies stocks at 52-week high or all-time high
3. Fetches sentiment only for stocks at highs
4. Generates AI analysis with recommendations
5. Saves all output to `output/` folder

### Individual Modules

```bash
python fetch_tickers.py   # Fetch ticker list
python snapshot.py        # Fetch price/high data only
python sentiment.py       # Fetch sentiment only
python agent.py           # Run AI analysis only
```

## Output Files

| File | Description |
|------|-------------|
| `output/snapshot.txt` | Current snapshot of all stocks |
| `output/stocks_at_highs.txt` | History of stocks at 52W high or ATH |
| `output/ai_analysis.md` | AI analysis with recommendations (newest at top) |

## AI Analysis Output

The AI analysis includes:

- **🏆 AT ALL-TIME HIGH** - All stocks at ATH (grouped by sentiment)
- **🔥 AT 52-WEEK HIGH ONLY** - Stocks at 52W high but not ATH
- **💡 AI RECOMMENDATIONS - TOP Stock PICKS** - Best stocks based on sentiment/momentum
- **💡 AI RECOMMENDATIONS - TECH & AI Stock PICKS** - Tech sector picks

## Key Metrics

| Metric | Description |
|--------|-------------|
| `% From 52W High` | Distance from 52-week high (0% = at high) |
| `% From ATH` | Distance from all-time high (0% = at ATH) |
| `At 52W High` | True if within 2% of 52-week high |
| `At ATH` | True if within 2% of all-time high |
| `Sentiment` | Bullish / Neutral / Bearish (based on news) |

## License

MIT License
