# 🇮🇳 Indian E-Commerce Sentiment Intelligence Platform

🔴 **Live Dashboard:** https://ananya-sentiment.streamlit.app

## What This Project Does
Tracks real-time public sentiment for **Zomato, Swiggy, Myntra 
and Amazon India** by fetching live YouTube comments and news 
headlines daily using APIs.

## Key Findings
- Myntra has the highest sentiment score (0.146) among all 4 brands
- Swiggy has the most negative posts — mainly delivery complaints
- News coverage is significantly more positive than YouTube 
  public comments for all brands
- Amazon India has the highest negative % (14%) despite strong sales

## Tech Stack
| Tool | Purpose |
|------|---------|
| Python | Core programming |
| YouTube Data API v3 | Live comment collection |
| NewsAPI | Live news headlines |
| VADER NLP | Sentiment scoring |
| SQLite + SQL | Data storage & analysis |
| Streamlit | Live dashboard deployment |
| Plotly | Interactive charts |

## How to Run Locally
1. Clone repo: `git clone https://github.com/Ananya8900/sentiment-intelligence`
2. Install: `pip install -r requirements.txt`
3. Add API keys to `config.py`
4. Run: `streamlit run app.py`

## Project Structure
```
sentiment-intelligence/
├── app.py              # Streamlit dashboard
├── collect.py          # Data collection pipeline  
├── analyze.py          # NLP sentiment scoring
├── queries.sql         # SQL business analysis
├── requirements.txt    # Dependencies
└── README.md           # This file
```