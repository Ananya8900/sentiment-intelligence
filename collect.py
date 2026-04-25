# collect.py - Fetches live YouTube comments + News headlines

from googleapiclient.discovery import build
from newsapi import NewsApiClient
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime
from config import *

# Connect to APIs
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
news_client = NewsApiClient(api_key=NEWS_API_KEY)

# Connect to database
engine = create_engine("sqlite:///sentiment.db")


def search_youtube_videos(brand):
    print(f"  Searching YouTube videos for: {brand}")
    request = youtube.search().list(
        q=brand + " review India",
        part="snippet",
        maxResults=10,
        type="video",
        relevanceLanguage="en",
        regionCode="IN"
    )
    response = request.execute()
    video_ids = [item["id"]["videoId"] for item in response["items"]]
    return video_ids


def fetch_youtube_comments(brand, video_ids):
    print(f"  Fetching comments for: {brand}")
    comments = []
    for vid_id in video_ids:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=vid_id,
                maxResults=50,
                textFormat="plainText"
            )
            response = request.execute()
            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "brand":   brand,
                    "source":  "YouTube",
                    "text":    comment["textDisplay"],
                    "upvotes": comment["likeCount"],
                    "date":    comment["publishedAt"],
                    "url":     f"https://youtube.com/watch?v={vid_id}"
                })
        except Exception as e:
            print(f"  Skipping video {vid_id}: {e}")
    return comments


def fetch_news(brand):
    print(f"  Fetching news for: {brand}")
    articles = []
    try:
        response = news_client.get_everything(
            q=brand,
            language="en",
            sort_by="publishedAt",
            page_size=50
        )
        for a in response["articles"]:
            text = (a["title"] or "") + " " + (a["description"] or "")
            articles.append({
                "brand":   brand,
                "source":  "News",
                "text":    text,
                "upvotes": 0,
                "date":    a["publishedAt"],
                "url":     a["url"]
            })
    except Exception as e:
        print(f"  News error for {brand}: {e}")
    return articles


def run_collection():
    print("Starting data collection...")
    all_data = []

    for brand in BRANDS:
        print(f"\nCollecting: {brand}")
        video_ids = search_youtube_videos(brand)
        all_data += fetch_youtube_comments(brand, video_ids)
        all_data += fetch_news(brand)

    df = pd.DataFrame(all_data)
    df["collected_at"] = datetime.now()
    df.to_sql("raw_data", engine, if_exists="append", index=False)
    print(f"\nDone! Saved {len(df)} posts to database.")


if __name__ == "__main__":
    run_collection()