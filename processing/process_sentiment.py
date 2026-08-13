"""
Loads raw YouTube + news data, cleans it, scores it with VADER,
and saves both the scored dataset and a brand-level summary.

Run from the project root (after running both collectors):
    python processing/process_sentiment.py
"""

import os
import sys
import re
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR

analyzer = SentimentIntensityAnalyzer()


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+", "", text)          # strip URLs
    text = re.sub(r"\s+", " ", text).strip()     # collapse whitespace
    return text


def label_from_score(compound):
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    return "Neutral"


def load_raw_data():
    frames = []
    yt_path = os.path.join(DATA_DIR, "youtube_raw.csv")
    news_path = os.path.join(DATA_DIR, "news_raw.csv")

    if os.path.exists(yt_path):
        frames.append(pd.read_csv(yt_path))
    if os.path.exists(news_path):
        frames.append(pd.read_csv(news_path))

    if not frames:
        raise FileNotFoundError(
            "No raw data found. Run the collectors first: "
            "collectors/youtube_collector.py and collectors/news_collector.py"
        )
    return pd.concat(frames, ignore_index=True, sort=False)


def main():
    df = load_raw_data()

    df["text"] = df["text"].apply(clean_text)
    df = df[df["text"].str.len() > 0]
    df = df.drop_duplicates(subset=["text", "brand", "source"])

    df["compound_score"] = df["text"].apply(
        lambda t: analyzer.polarity_scores(t)["compound"]
    )
    df["sentiment"] = df["compound_score"].apply(label_from_score)

    scored_path = os.path.join(DATA_DIR, "scored_data.csv")
    df.to_csv(scored_path, index=False)
    print(f"Saved {len(df)} scored rows to {scored_path}")

    summary = (
        df.groupby("brand")
        .agg(
            avg_sentiment=("compound_score", "mean"),
            mentions=("text", "count"),
            positive_pct=("sentiment", lambda s: (s == "Positive").mean() * 100),
            negative_pct=("sentiment", lambda s: (s == "Negative").mean() * 100),
            neutral_pct=("sentiment", lambda s: (s == "Neutral").mean() * 100),
        )
        .reset_index()
        .sort_values("avg_sentiment", ascending=False)
    )

    summary_path = os.path.join(DATA_DIR, "brand_summary.csv")
    summary.to_csv(summary_path, index=False)
    print(f"Saved brand summary to {summary_path}")


if __name__ == "__main__":
    main()
