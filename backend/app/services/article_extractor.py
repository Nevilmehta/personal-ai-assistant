from typing import Optional
from urllib.parse import urlparse

import requests
import trafilatura
from bs4 import BeautifulSoup
from newspaper import Article as NewspaperArticle


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def is_google_news_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return "news.google.com" in parsed.netloc
    except Exception:
        return False


def resolve_final_url(url: str, timeout: int = 15) -> str:
    """
    Tries to follow redirects and return the final publisher URL.

    Google News RSS links are often wrapper links. Sometimes requests can
    resolve them, sometimes Google keeps us on a wrapper page.
    """
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )

        final_url = response.url

        if final_url:
            return final_url

        return url

    except Exception:
        return url


def fetch_url_html(url: str, timeout: int = 15) -> Optional[str]:
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )

        response.raise_for_status()

        if "text/html" not in response.headers.get("content-type", ""):
            return None

        return response.text

    except Exception:
        return None


def extract_with_trafilatura(html: str) -> Optional[str]:
    try:
        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            favor_precision=False,
        )

        if text and len(text.strip()) >= 300:
            return text.strip()

        return None

    except Exception:
        return None


def extract_with_newspaper(url: str) -> Optional[str]:
    try:
        article = NewspaperArticle(url)
        article.download()
        article.parse()

        text = article.text

        if text and len(text.strip()) >= 300:
            return text.strip()

        return None

    except Exception:
        return None


def extract_with_bs4(html: str) -> Optional[str]:
    try:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.decompose()

        paragraphs = [
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
        ]

        paragraphs = [
            p for p in paragraphs
            if len(p) > 60
        ]

        text = "\n".join(paragraphs).strip()

        if len(text) >= 300:
            return text

        return None

    except Exception:
        return None


def extract_article_text(url: str) -> tuple[Optional[str], str]:
    """
    Returns:
    - extracted article text
    - final resolved URL
    """

    final_url = resolve_final_url(url)

    html = fetch_url_html(final_url)

    if html:
        trafilatura_text = extract_with_trafilatura(html)

        if trafilatura_text:
            return trafilatura_text, final_url  

    newspaper_text = extract_with_newspaper(final_url)

    if newspaper_text:
        return newspaper_text, final_url

    if html:
        bs4_text = extract_with_bs4(html)

        if bs4_text:
            return bs4_text, final_url

    return None, final_url

def trim_article_text(text: str, max_chars: int = 6000) -> str:
    if len(text) <= max_chars:
        return text

    return text[:max_chars].rsplit(" ", 1)[0] + "..."