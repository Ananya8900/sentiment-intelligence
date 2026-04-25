# analyze.py - Cleans text and scores sentiment

import re
import pandas as pd
from sqlalchemy import create_engine
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

engine   = create_engine("sqlite:///sentiment.db")
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


def run_analysis():
    print("Loading data...")
    df = pd.read_sql("SELECT * FROM raw_data", engine)
    print(f"Scoring sentiment for {len(df)} posts...")

    df["clean_text"]      = df["text"].apply(clean_text)
    df["sentiment_score"] = df["clean_text"].apply(lambda x: score_sentiment(x)[0])
    df["sentiment_label"] = df["clean_text"].apply(lambda x: score_sentiment(x)[1])

    df.to_sql("analyzed_data", engine, if_exists="replace", index=False)
    print(f"Done! All {len(df)} posts scored.")

    print("\n--- Sentiment Summary ---")
    summary = df.groupby(["brand", "sentiment_label"]).size().unstack(fill_value=0)
    print(summary)


if __name__ == "__main__":
    run_analysis()