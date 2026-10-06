# 📊 Real-Time Sentiment Analysis on Twitter Data

A simple Streamlit dashboard that pulls tweets for a keyword/hashtag, cleans the text, scores sentiment with **VADER**, and visualizes the results live.

## Features
- Collects tweets via the Twitter (X) API v2 using `tweepy`
- Cleans text (removes links, @mentions, RT, `#`, extra spaces)
- Sentiment analysis with VADER (Positive / Neutral / Negative)
- Live dashboard: metrics, sentiment pie chart, trend line, tweet table
- Auto-refresh mode for "real-time" updates
- **Demo mode** – works without an API key using sample tweets

## Project Structure
```
├── app.py             # whole app (collect → clean → analyze → dashboard)
├── requirements.txt
├── .env.example       # copy to .env and add your token
└── .gitignore
```

## Setup
```bash
git clone https://github.com/<your-username>/twitter-sentiment-dashboard.git
cd twitter-sentiment-dashboard
pip install -r requirements.txt
```

### (Optional) Add your Twitter API token
1. Get a **Bearer Token** from the [X Developer Portal](https://developer.x.com/).
2. Copy `.env.example` to `.env` and paste your token:
   ```
   TWITTER_BEARER_TOKEN=your_token_here
   ```
Without a token, the app runs in demo mode.

## Run
```bash
streamlit run app.py
```
Open http://localhost:8501, enter a keyword/hashtag, and tick **Auto-refresh** for live updates.

## How It Works
| Step | Tool |
|------|------|
| Data collection | `tweepy` → `search_recent_tweets` |
| Text cleaning | Python `re` (regex) |
| Sentiment | VADER compound score (≥ 0.05 positive, ≤ -0.05 negative) |
| Dashboard | Streamlit + Plotly |

## Notes
- The free X API tier has very strict rate limits; use a longer refresh interval if you hit them.
- Never commit your `.env` file (it's in `.gitignore`).

## License
MIT
