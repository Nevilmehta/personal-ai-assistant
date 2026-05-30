import hashlib
from typing import List, Optional

def generate_text_hash(text: str):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150):
    """
    Splits long text into overlapping chunks.

    Example:
    chunk 1: chars 0-1000
    chunk 2: chars 850-1850
    chunk 3: chars 1700-2700
    """

    if not text or not text.strip():
        return []

    cleaned_text = " ".join(text.split())

    if len(cleaned_text) <= chunk_size:
        return [cleaned_text]

    chunks = []
    start = 0

    while start < len(cleaned_text):
        end = start + chunk_size
        chunk = cleaned_text[start:end]

        # Avoid cutting in the middle of a word if possible
        if end < len(cleaned_text):
            last_space = chunk.rfind(" ")
            if last_space > 0:
                chunk = chunk[:last_space]
                end = start + last_space

        chunks.append(chunk.strip())
        start = max(end - overlap, start + 1)

    return chunks