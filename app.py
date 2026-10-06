"""Real-Time Sentiment Analysis on Twitter (X) Data - Streamlit dashboard."""
import os
import random
import re
import time
import uuid
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
import tweepy
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

load_dotenv()
analyzer = SentimentIntensityAnalyzer()

COLORS = {"Positive": "#2ecc71", "Neutral": "#95a5a6", "Negative": "#e74c3c"}


# ---------- 1. Collect data ----------
def demo_tweets(n):
    """Fake tweets so the app works without a Twitter API key."""
    samples = [
        "I absolutely love this! Best thing ever 😍",
        "This is terrible, I want my money back.",
        "Just saw the news. Not sure how I feel about it.",
        "Amazing update, great job by the team! #win",
        "Worst experience of my life. So disappointed 😡",
        "It's okay, nothing special.",
        "Can't wait for tomorrow, so excited!!!",
        "Totally overrated. Waste of time.",
    ]
    return [
        {"id": str(uuid.uuid4()), "time": datetime.now(), "text": random.choice(samples)}
        for _ in range(min(n, 15))
    ]


def get_tweets(query, n):
    token = os.getenv("TWITTER_BEARER_TOKEN")
    if not token:
        return demo_tweets(n)
    client = tweepy.Client(bearer_token=token)
    resp = client.search_recent_tweets(
        query=f"{query} -is:retweet lang:en",
        max_results=max(10, min(n, 100)),
        tweet_fields=["created_at"],
    )
    return [{"id": str(t.id), "time": t.created_at, "text": t.text} for t in (resp.data or [])]


# ---------- 2. Clean text ----------
def clean_text(text):
    text = re.sub(r"http\S+|www\.\S+", "", text)   # links
    text = re.sub(r"@\w+", "", text)               # mentions
    text = re.sub(r"^RT\s+", "", text)             # retweet marker
    text = text.replace("#", "")                   # keep hashtag word, drop symbol
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------- 3. Sentiment (VADER) ----------
def label(score):
    if score >= 0.05:
        return "Positive"
    if score <= -0.05:
        return "Negative"
    return "Neutral"


def analyze(tweets):
    df = pd.DataFrame(tweets)
    df["clean"] = df["text"].apply(clean_text)
    df["score"] = df["clean"].apply(lambda t: analyzer.polarity_scores(t)["compound"])
    df["sentiment"] = df["score"].apply(label)
    return df


# ---------- 4. Dashboard ----------
st.set_page_config(page_title="Twitter Sentiment", page_icon="📊", layout="wide")
st.title("📊 Real-Time Twitter Sentiment Analysis")

with st.sidebar:
    query = st.text_input("Keyword / hashtag", "python")
    count = st.slider("Tweets per fetch", 10, 100, 20)
    auto = st.checkbox("Auto-refresh", value=False)
    interval = st.slider("Refresh every (seconds)", 15, 120, 30)
    if st.button("Clear data"):
        st.session_state.pop("df", None)

if not os.getenv("TWITTER_BEARER_TOKEN"):
    st.info("No `TWITTER_BEARER_TOKEN` found - showing **demo data**. See README to use real tweets.")

# Reset stored data when the keyword changes
if st.session_state.get("query") != query:
    st.session_state["query"] = query
    st.session_state.pop("df", None)

# Fetch + analyze + append new tweets
try:
    new = get_tweets(query, count)
    if new:
        new_df = analyze(new)
        old_df = st.session_state.get("df", pd.DataFrame())
        df = pd.concat([old_df, new_df]).drop_duplicates("id").tail(500)
        st.session_state["df"] = df
except tweepy.TooManyRequests:
    st.warning("Twitter rate limit reached. Wait a few minutes and try again.")
except Exception as e:
    st.error(f"Error fetching tweets: {e}")

df = st.session_state.get("df")

if df is None or df.empty:
    st.write("No tweets yet.")
else:
    counts = df["sentiment"].value_counts()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total tweets", len(df))
    c2.metric("Positive 😊", int(counts.get("Positive", 0)))
    c3.metric("Neutral 😐", int(counts.get("Neutral", 0)))
    c4.metric("Negative 😠", int(counts.get("Negative", 0)))

    left, right = st.columns(2)
    with left:
        pie = px.pie(
            names=counts.index, values=counts.values, hole=0.4,
            color=counts.index, color_discrete_map=COLORS, title="Sentiment split",
        )
        st.plotly_chart(pie, use_container_width=True)
    with right:
        trend = df.sort_values("time").reset_index(drop=True)
        trend["rolling avg"] = trend["score"].rolling(10, min_periods=1).mean()
        line = px.line(trend, y="rolling avg", title="Average sentiment over time (-1 to +1)")
        st.plotly_chart(line, use_container_width=True)

    st.subheader("Latest tweets")
    st.dataframe(
        df.sort_values("time", ascending=False)[["time", "clean", "score", "sentiment"]],
        use_container_width=True, hide_index=True,
    )

if auto:
    time.sleep(interval)
    st.rerun()
