"""
Central place to control which brands you're tracking.
Start with 2 brands while you're testing, then expand.
"""

BRANDS = [
    "Flipkart",
    "Amazon India",
    "Myntra",
    # "Meesho",
    # "Nykaa",
]

# How many YouTube videos to pull per brand per run
VIDEOS_PER_BRAND = 15

# How many comments to pull per video
COMMENTS_PER_VIDEO = 50

# How many news articles to pull per brand per run (before relevance filtering)
ARTICLES_PER_BRAND = 50

DATA_DIR = "data"
