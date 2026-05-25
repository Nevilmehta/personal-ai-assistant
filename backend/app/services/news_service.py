from typing import List, Dict
from urllib.parse import quote_plus
import feedparser

from app.services.article_extractor import extract_article_text, trim_article_text

def search_news(query: str, max_results: int = 8):
    encoded_query = quote_plus(query)

    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    )

    feed = feedparser.parse(rss_url)

    articles = []

    for entry in feed.entries[:max_results]:
        article = {
            "title": entry.get("title", "No title"),
            "url": entry.get("link", ""),
            "published": entry.get("published", None),
            "source": "Google News RSS",
            "summary": entry.get("summary", ""),
            "content": None,
            "content_available": False,
        }

        articles.append(article)

    return articles

def enrich_articles_with_content(
    articles: List[Dict],
    max_articles_to_fetch: int = 5,
):
    enriched_articles = []

    for index, article in enumerate(articles):
        if index < max_articles_to_fetch and article.get("url"):
            article_text = extract_article_text(article["url"])

            if article_text:
                article["content"] = trim_article_text(article_text)
                article["content_available"] = True

        enriched_articles.append(article)

    return enriched_articles

def deduplicate_articles(articles: List[Dict]):
    seen_titles = set()
    unique_articles = []

    for article in articles:
        title = article.get("title", "").lower().strip()

        normalized_title = (
            title.replace(" - ", " ")
            .replace(" | ", " ")
            .replace(" , ", " ")
            .replace(":", " ")
        )

        title_key = " ".join(normalized_title.split()[:10])
        if title_key in seen_titles:
            continue

        seen_titles.add(title_key)
        unique_articles.append(article)

    return unique_articles

def rank_articles(articles: List[Dict]):
    def score_article(article: Dict):
        score = 0

        if article.get("content_available"):
            score += 5

        if article.get("published"):
            score += 2

        if article.get("title"):
            score += 1

        if article.get("summary"):
            score += 1

        return score

    return sorted(articles, key=score_article, reverse=True)

def get_intelligent_news_context(
    query: str,
    max_results: int = 8,
    max_articles_to_fetch: int = 5
):
    articles = search_news(query=query, max_results=max_results)

    articles = deduplicate_articles(articles)
    articles = enrich_articles_with_content(
        articles=articles,
        max_articles_to_fetch=max_articles_to_fetch
    )

    articles = rank_articles(articles)
    return articles[:max_results]