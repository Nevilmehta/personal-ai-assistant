from typing import List, Dict
from urllib.parse import quote_plus
import feedparser

def search_news(query: str, max_results: int = 5):
    encoded_query = quote_plus(query)

    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    )

    feed = feedparser.parse(rss_url)

    articles = []

    for entry in feed.entries[:max_results]:
        articles.append({
            "title": entry.get("title", "No title"),
            "url": entry.get("link", ""),
            "published": entry.get("published", None),
            "source": "Google News RSS",
            "summary": entry.get("summary", ""),
        })
    
    return articles