import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
from googleapiclient.discovery import build
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

st.set_page_config(
    page_title="Indian Brand Sentiment Dashboard",
    page_icon="📊",
    layout="wide"
)

BRANDS = ["Zomato", "Swiggy", "Myntra", "Amazon India"]

# Get keys from Streamlit secrets or config
try:
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
    NEWS_API_KEY    = st.secrets["NEWS_API_KEY"]
except:
    from config import YOUTUBE_API_KEY, NEWS_API_KEY

analyzer = SentimentIntensityAnalyzer()

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def score_sentiment(text):
    score = analyzer.polarity_scores(text)["compound"]
    if   score >=  0.05: label = "Positive"
    elif score <= -0.05: label = "Negative"
    else:                label = "Neutral"
    return score, label

@st.cache_data(ttl=3600, show_spinner="Fetching live data...")
def load_live_data():
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    news_client = NewsApiClient(api_key=NEWS_API_KEY)
    all_data = []

    for brand in BRANDS:
        # YouTube
        try:
            res = youtube.search().list(
                q=brand + " review India",
                part="snippet", maxResults=5,
                type="video", regionCode="IN"
            ).execute()
            video_ids = [i["id"]["videoId"] for i in res["items"]]
            for vid_id in video_ids:
                try:
                    comments = youtube.commentThreads().list(
                        part="snippet", videoId=vid_id,
                        maxResults=30, textFormat="plainText"
                    ).execute()
                    for item in comments["items"]:
                        c = item["snippet"]["topLevelComment"]["snippet"]
                        all_data.append({
                            "brand": brand, "source": "YouTube",
                            "text": c["textDisplay"],
                            "upvotes": c["likeCount"],
                            "date": c["publishedAt"]
                        })
                except: pass
        except: pass

        # News
        try:
            articles = news_client.get_everything(
                q=brand, language="en",
                sort_by="publishedAt", page_size=30
            )
            for a in articles["articles"]:
                text = (a["title"] or "") + " " + (a["description"] or "")
                all_data.append({
                    "brand": brand, "source": "News",
                    "text": text, "upvotes": 0,
                    "date": a["publishedAt"]
                })
        except: pass

    df = pd.DataFrame(all_data)
    df["clean_text"]      = df["text"].apply(clean_text)
    df["sentiment_score"] = df["clean_text"].apply(lambda x: score_sentiment(x)[0])
    df["sentiment_label"] = df["clean_text"].apply(lambda x: score_sentiment(x)[1])
    return df

df = load_live_data()

# ── SIDEBAR ──
st.sidebar.title("🔍 Filters")
brands = st.sidebar.multiselect(
    "Select Brands", options=BRANDS, default=BRANDS)
source = st.sidebar.radio("Data Source", ["All", "YouTube", "News"])

filtered = df[df["brand"].isin(brands)]
if source != "All":
    filtered = filtered[filtered["source"] == source]

# ── HEADER ──
st.title("🇮🇳 Indian E-Commerce Sentiment Intelligence")
st.caption("Real-time brand perception — Zomato · Swiggy · Myntra · Amazon India")
st.divider()

# ── KPI CARDS ──
cols = st.columns(len(brands))
for i, brand in enumerate(brands):
    bdf = filtered[filtered["brand"] == brand]
    if len(bdf) > 0:
        score = bdf["sentiment_score"].mean()
        pos = (bdf["sentiment_label"] == "Positive").mean() * 100
        neg = (bdf["sentiment_label"] == "Negative").mean() * 100
        cols[i].metric(
            label=f"**{brand}**",
            value=f"{score:.3f}",
            delta=f"{pos:.0f}% pos / {neg:.0f}% neg"
        )

st.divider()

# ── CHARTS ──
col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Sentiment Breakdown")
    breakdown = filtered.groupby(
        ["brand","sentiment_label"]).size().reset_index(name="count")
    fig1 = px.bar(breakdown, x="brand", y="count",
        color="sentiment_label",
        color_discrete_map={"Positive":"#1D9E75","Neutral":"#AAAAAA","Negative":"#E24B4A"},
        barmode="group")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📰 YouTube vs News")
    sc = filtered.groupby(["brand","source"])["sentiment_score"].mean().reset_index()
    fig2 = px.bar(sc, x="brand", y="sentiment_score", color="source",
        barmode="group",
        color_discrete_map={"YouTube":"#FF0000","News":"#1A5EA5"})
    fig2.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("😡 Most Liked Negative Posts")
worst = filtered[filtered["sentiment_label"]=="Negative"].nlargest(10,"upvotes")
st.dataframe(worst[["brand","source","text","upvotes","sentiment_score"]], use_container_width=True)

st.subheader("😊 Most Liked Positive Posts")
best = filtered[filtered["sentiment_label"]=="Positive"].nlargest(10,"upvotes")
st.dataframe(best[["brand","source","text","upvotes","sentiment_score"]], use_container_width=True)

st.caption(f"Total posts: {len(filtered):,} | Updates every hour automatically")