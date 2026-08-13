"""
Pulls recent news headlines/descriptions mentioning each brand.
Saves raw results to data/news_raw.csv

Run from the project root:
    python collectors/news_collector.py
"""

import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BRANDS, ARTICLES_PER_BRAND, DATA_DIR

load_dotenv()
API_KEY = os.getenv("NEWSAPI_KEY")
BASE_URL = "https://newsapi.org/v2/everything"


def fetch_articles(brand, page_size):
    params = {
        "q": f'"{brand}"',
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    articles = resp.json().get("articles", [])

    # NewsAPI's phrase matching is loose even with quotes, so double-check
    # the brand name actually appears in the title or description before keeping it.
    brand_lower = brand.lower()
    filtered = []
    for a in articles:
        title = (a.get("title") or "").lower()
        desc = (a.get("description") or "").lower()
        if brand_lower in title or brand_lower in desc:
            filtered.append(a)
    return filtered


def main():
    if not API_KEY:
        raise RuntimeError("NEWSAPI_KEY not found. Did you create a .env file?")

    os.makedirs(DATA_DIR, exist_ok=True)
    rows = []

    for brand in BRANDS:
        print(f"Fetching news data for: {brand}")
        try:
            articles = fetch_articles(brand, ARTICLES_PER_BRAND)
        except requests.exceptions.HTTPError as e:
            print(f"  Fetch failed for {brand}: {e}")
            continue

        for a in articles:
            text = f"{a.get('title', '')}. {a.get('description', '') or ''}".strip()
            rows.append({
                "brand": brand,
                "source": "news",
                "text": text,
                "url": a.get("url"),
                "published_at": a.get("publishedAt"),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })
        time.sleep(0.2)

    df = pd.DataFrame(rows)
    out_path = os.path.join(DATA_DIR, "news_raw.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} articles to {out_path}")


if __name__ == "__main__":
    main()