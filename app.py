# app.py - Your live Streamlit dashboard

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(
    page_title="Indian Brand Sentiment Dashboard",
    page_icon="📊",
    layout="wide"
)

engine = create_engine("sqlite:///sentiment.db")

@st.cache_data(ttl=3600)
def load_data():
    return pd.read_sql("SELECT * FROM analyzed_data", engine)

df = load_data()

# ── SIDEBAR ──
st.sidebar.title("🔍 Filters")
brands = st.sidebar.multiselect(
    "Select Brands",
    options=df["brand"].unique(),
    default=list(df["brand"].unique())
)
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
    score = bdf["sentiment_score"].mean()
    pos = (bdf["sentiment_label"] == "Positive").mean() * 100
    neg = (bdf["sentiment_label"] == "Negative").mean() * 100
    cols[i].metric(
        label=f"**{brand}**",
        value=f"{score:.3f}",
        delta=f"{pos:.0f}% positive / {neg:.0f}% negative"
    )

st.divider()

# ── SENTIMENT BREAKDOWN ──
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Sentiment Breakdown by Brand")
    breakdown = filtered.groupby(
        ["brand", "sentiment_label"]
    ).size().reset_index(name="count")
    fig1 = px.bar(
        breakdown, x="brand", y="count",
        color="sentiment_label",
        color_discrete_map={
            "Positive": "#1D9E75",
            "Neutral":  "#AAAAAA",
            "Negative": "#E24B4A"
        },
        barmode="group",
        title="Positive vs Neutral vs Negative per Brand"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🥧 Sentiment Share per Brand")
    pie_data = filtered.groupby(
        ["brand", "sentiment_label"]
    ).size().reset_index(name="count")
    fig2 = px.sunburst(
        pie_data, path=["brand", "sentiment_label"],
        values="count",
        color="sentiment_label",
        color_discrete_map={
            "Positive": "#1D9E75",
            "Neutral":  "#AAAAAA",
            "Negative": "#E24B4A"
        },
        title="Overall Sentiment Distribution"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── SOURCE COMPARISON ──
st.subheader("📰 YouTube Comments vs News Headlines")
source_comp = filtered.groupby(
    ["brand", "source"]
)["sentiment_score"].mean().reset_index()
fig3 = px.bar(
    source_comp, x="brand",
    y="sentiment_score", color="source",
    barmode="group",
    title="Media Sentiment vs Public Sentiment",
    color_discrete_map={
        "YouTube": "#FF0000",
        "News":    "#1A5EA5"
    }
)
fig3.add_hline(y=0, line_dash="dash", line_color="gray")
st.plotly_chart(fig3, use_container_width=True)

# ── WORST POSTS ──
st.subheader("😡 Most Liked Negative Posts")
worst = filtered[
    filtered["sentiment_label"] == "Negative"
].nlargest(10, "upvotes")[["brand","source","text","upvotes","sentiment_score"]]
st.dataframe(worst, use_container_width=True)

# ── BEST POSTS ──
st.subheader("😊 Most Liked Positive Posts")
best = filtered[
    filtered["sentiment_label"] == "Positive"
].nlargest(10, "upvotes")[["brand","source","text","upvotes","sentiment_score"]]
st.dataframe(best, use_container_width=True)

st.divider()
st.caption(f"Total posts analyzed: {len(filtered):,}  |  Sources: YouTube + NewsAPI  |  Updates daily")