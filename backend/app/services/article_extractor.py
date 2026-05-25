from typing import Optional
import requests
import trafilatura

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

def fetch_url_html(url: str, timeout: int = 10):
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception:
        return None

def extract_article_text(url: str):
    html = fetch_url_html(url)

    if not html:
        return None

    text = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
    )

    if not text:
        return None

    cleaned = text.strip()

    if len(cleaned) < 300:
        return None

    return cleaned

def trim_article_text(text: str, max_chars: int = 4000):
    if len(text) <= max_chars:
        return text

    return text[:max_chars].rsplit(" ", 1)[0] + "..."