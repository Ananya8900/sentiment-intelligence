"""
Streamlit dashboard for the multi-brand sentiment data.

Run from the project root:
    streamlit run dashboard/app.py
"""

import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR

st.set_page_config(page_title="Brand Sentiment Dashboard", layout="wide")


@st.cache_data(ttl=3600)
def load_data():
    scored = pd.read_csv(os.path.join(DATA_DIR, "scored_data.csv"))
    summary = pd.read_csv(os.path.join(DATA_DIR, "brand_summary.csv"))
    return scored, summary


st.title("📊 Multi-Brand Sentiment Dashboard")
st.caption("Live sentiment tracking across YouTube and news mentions for Indian e-commerce brands")

try:
    scored_df, summary_df = load_data()
except FileNotFoundError:
    st.error(
        "No processed data found yet. Run the collectors and "
        "processing/process_sentiment.py first, then refresh this page."
    )
    st.stop()

brands = sorted(scored_df["brand"].unique())
selected_brand = st.selectbox("Select a brand", ["All brands"] + brands)

filtered = scored_df if selected_brand == "All brands" else scored_df[scored_df["brand"] == selected_brand]

col1, col2, col3 = st.columns(3)
col1.metric("Total mentions", len(filtered))
col2.metric("Avg sentiment score", f"{filtered['compound_score'].mean():.2f}")
col3.metric("% Positive", f"{(filtered['sentiment'] == 'Positive').mean() * 100:.1f}%")

st.subheader("Average sentiment by brand")
fig1 = px.bar(
    summary_df, x="brand", y="avg_sentiment", color="avg_sentiment",
    color_continuous_scale="RdYlGn", labels={"avg_sentiment": "Avg. Sentiment Score"},
)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Sentiment breakdown by brand")
melted = summary_df.melt(
    id_vars="brand",
    value_vars=["positive_pct", "neutral_pct", "negative_pct"],
    var_name="sentiment", value_name="percentage",
)
fig2 = px.bar(
    melted, x="brand", y="percentage", color="sentiment", barmode="stack",
    color_discrete_map={"positive_pct": "#2ecc71", "neutral_pct": "#95a5a6", "negative_pct": "#e74c3c"},
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Most positive & negative mentions")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Top positive**")
    st.dataframe(
        filtered.sort_values("compound_score", ascending=False)[["brand", "source", "text", "compound_score"]].head(5),
        hide_index=True,
    )
with c2:
    st.markdown("**Top negative**")
    st.dataframe(
        filtered.sort_values("compound_score")[["brand", "source", "text", "compound_score"]].head(5),
        hide_index=True,
    )
