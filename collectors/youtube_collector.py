"""
Pulls recent YouTube videos + top-level comments mentioning each brand.
Saves raw results to data/youtube_raw.csv

Run from the project root:
    python collectors/youtube_collector.py
"""

import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BRANDS, VIDEOS_PER_BRAND, COMMENTS_PER_VIDEO, DATA_DIR

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"


def search_videos(query, max_results):
    """Find recent video IDs mentioning the brand."""
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "date",
        "maxResults": max_results,
        "key": API_KEY,
    }
    resp = requests.get(f"{BASE_URL}/search", params=params, timeout=15)
    resp.raise_for_status()
    return [item["id"]["videoId"] for item in resp.json().get("items", [])]


def get_comments(video_id, max_results):
    """Pull top-level comments for a video. Skips videos with comments disabled."""
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": max_results,
        "order": "relevance",
        "textFormat": "plainText",
        "key": API_KEY,
    }
    try:
        resp = requests.get(f"{BASE_URL}/commentThreads", params=params, timeout=15)
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        return []  # comments disabled or video restricted — skip quietly

    comments = []
    for item in resp.json().get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comments.append(snippet["textDisplay"])
    return comments


def main():
    if not API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY not found. Did you create a .env file?")

    os.makedirs(DATA_DIR, exist_ok=True)
    rows = []

    for brand in BRANDS:
        print(f"Fetching YouTube data for: {brand}")
        try:
            video_ids = search_videos(brand, VIDEOS_PER_BRAND)
        except requests.exceptions.HTTPError as e:
            print(f"  Search failed for {brand}: {e}")
            continue

        for vid in video_ids:
            comments = get_comments(vid, COMMENTS_PER_VIDEO)
            for text in comments:
                rows.append({
                    "brand": brand,
                    "source": "youtube",
                    "text": text,
                    "video_id": vid,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                })
            time.sleep(0.2)  # be polite to the API

    df = pd.DataFrame(rows)
    out_path = os.path.join(DATA_DIR, "youtube_raw.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} comments to {out_path}")


if __name__ == "__main__":
    main()
