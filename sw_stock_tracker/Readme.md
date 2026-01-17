# sw_tracker (sw_stock_tracker)
**Latest recommendation is at** [recommendations.md](https://github.com/jaglinux/python-projects/blob/c2748eb88d6bd0082ef56e8330bb0f3c87865e66/sw_stock_tracker/recommendations.md)

sw_tracker is a small Python toolkit to snapshot a list of software / SaaS-related stock quotes, compute simple changes, fetch sentiment from recent news, and generate short AI-driven daily buy recommendations (appended to a markdown log).

This project combines:
- `snapshot.py` — fetches current quotes and exports a table image
- `sentiment.py` — fetches headlines and computes VADER sentiment
- `tracker.py` — orchestrates snapshots, history, and change computation
- `agent.py` — uses LangChain + an OpenAI model to generate concise buy recommendations
- `stock_history.txt` — CSV log of snapshots over time
- `recommendations.md` — appended log of timestamped AI recommendations

## Quick overview

- Snapshot current prices and export `stocks_table.png` with `snapshot.py`.
- Fetch headlines and compute sentiment with `sentiment.py`.
- Track history and compute daily/weekly deltas with `tracker.py`.
- Generate AI recommendations and append them to `recommendations.md` with `agent.py`.


