# Multi-Brand Sentiment Dashboard — Setup Guide

Everything below is free. Follow it in order.

## 1. Get your API keys

**YouTube Data API v3**
1. Go to https://console.cloud.google.com/
2. Create a new project (any name).
3. Go to "APIs & Services" → "Library" → search "YouTube Data API v3" → Enable.
4. Go to "APIs & Services" → "Credentials" → "Create Credentials" → "API Key".
5. Copy the key.

**NewsAPI**
1. Go to https://newsapi.org/register
2. Sign up with your email (free Developer plan).
3. Copy your API key from the dashboard.

## 2. Set up the project

```bash
# from inside this folder
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# now open .env and paste in your two real API keys
```

## 3. Edit your brand list

Open `config.py` and set the brands you want to track (2–3 is enough to start).

## 4. Collect data

```bash
python collectors/youtube_collector.py
python collectors/news_collector.py
```

This creates `data/youtube_raw.csv` and `data/news_raw.csv`.

## 5. Process and score

```bash
python processing/process_sentiment.py
```

This creates `data/scored_data.csv` (every comment/article + its sentiment) and
`data/brand_summary.csv` (aggregated per-brand stats).

## 6. Run the dashboard locally

```bash
streamlit run dashboard/app.py
```

It opens at `http://localhost:8501`.

## 7. Push to GitHub

```bash
git init
echo "venv/" >> .gitignore
echo ".env" >> .gitignore
git add .
git commit -m "Multi-brand sentiment dashboard"
git branch -M main
git remote add origin https://github.com/Ananya8900/sentiment-intelligence.git
git push -u origin main --force
```

**Important:** `.env` must be in `.gitignore` — never push real API keys to GitHub.

## 8. Deploy for free on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click "New app" → pick your `sentiment-intelligence` repo → set main file path to
   `dashboard/app.py`.
3. Under "Advanced settings" → "Secrets", paste:
   ```
   YOUTUBE_API_KEY = "your_real_key"
   NEWSAPI_KEY = "your_real_key"
   ```
4. Deploy. You'll get a public URL like `your-app-name.streamlit.app`.

Note: for the deployed version to read secrets the same way `.env` does locally,
add this near the top of `dashboard/app.py` (Streamlit Cloud injects `st.secrets`
automatically, but your collector scripts run locally so `.env` is only needed
for those):

```python
import os
os.environ.setdefault("YOUTUBE_API_KEY", st.secrets.get("YOUTUBE_API_KEY", ""))
```

## 9. Keeping data fresh

Since collection runs locally (to protect your API keys and quota), refresh
the data every few days by re-running steps 4–5, then push the updated CSVs
in `data/` to GitHub — the deployed dashboard will pick up the new files
automatically.

## Free-tier limits to respect

- YouTube Data API: 10,000 quota units/day (a `search` call = 100 units, so
  keep `VIDEOS_PER_BRAND` small in `config.py`).
- NewsAPI free plan: 100 requests/day, articles from the last month only.
- Streamlit Community Cloud: 1 always-on public app, sleeps after inactivity,
  wakes on next visit.
