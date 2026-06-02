import hashlib
from typing import List, Optional
from bs4 import BeautifulSoup

def generate_text_hash(text: str):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def clean_text(raw_text: str):
    if not raw_text:
        return ""

    soup = BeautifulSoup(raw_text, "html.parser")
    plain_text = soup.get_text(" ", strip=True)

    return " ".join(plain_text.split())

def chunk_text(
    text: str,
    chunk_size: int = 700,
    overlap: int = 100,
):
    if not text or not text.strip():
        return []

    cleaned_text = clean_text(text)

    if len(cleaned_text) <= chunk_size:
        return [cleaned_text]

    chunks = []
    start = 0

    while start < len(cleaned_text):
        end = min(start + chunk_size, len(cleaned_text))
        chunk = cleaned_text[start:end]

        if end < len(cleaned_text):
            last_space = chunk.rfind(" ")

            if last_space > 0:
                chunk = chunk[:last_space]
                end = start + last_space

        chunk = chunk.strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(cleaned_text):
            break

        start = max(end - overlap, start + 1)

    return chunks