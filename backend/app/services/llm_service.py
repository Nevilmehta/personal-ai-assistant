import json
from typing import List, Dict
from google import genai
from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def answer_with_rag_context(user_query: str, retrieved_chunks: List[Dict]):
    if not settings.GEMINI_API_KEY:
        return (
            "Gemini API key is missing. "
            "Please add GEMINI_API_KEY to your .env file."
        )

    if not retrieved_chunks:
        return (
            "I could not find enough relevant information "
            "in my stored knowledge base to answer that."
        )

    context_items = []
    for index, result in enumerate(retrieved_chunks, start=1):
        payload = result.get("payload", {})

        context_items.append(
            {
                "reference": f"Source {index}",
                "title": payload.get("title"),
                "publisher": payload.get("source"),
                "published": payload.get("published"),
                "url": payload.get("url"),
                "content_quality": payload.get("content_quality", "unknown"),
                "text": payload.get("text", ""),
            }
        )

    context_json = json.dumps(
        context_items,
        indent=2,
        ensure_ascii=False,
    )

    prompt = f"""
You are Jarvis, a personal AI intelligence assistant.

Answer the user's question using only the retrieved knowledge-base context.

User question:
{user_query}

Retrieved context:
{context_json}

Instructions:
- Use only the supplied context.
- Do not invent facts, events, quotes, numbers, or dates.
- If context is insufficient, say so clearly.
- If sources repeat the same event, combine them.
- Mention uncertainty when the context is limited.
- Cite supporting context inline using labels such as [Source 1].
- Keep the answer clear and conversational.
- End with a short "Main takeaway" sentence.
"""

    response = client.models.generate_content(
        model = settings.GEMINI_MODEL,
        contents = prompt
    )

    return response.text or "I could not generate a response."

def summarize_news(user_query: str, articles: List[Dict]) -> str:
    if not settings.GEMINI_API_KEY:
        return "Gemini API key is missing. Please add GEMINI_API_KEY in your .env file."

    if not articles:
        return "I could not find recent news for this query."

    compact_articles = []

    for article in articles:
        compact_articles.append(
            {
                "title": article.get("title"),
                "published": article.get("published"),
                "source": article.get("source"),
                "url": article.get("url"),
                "snippet": article.get("summary"),
                "content_available": article.get("content_available", False),
                "content": article.get("content"),
            }
        )

    article_context = json.dumps(
        compact_articles,
        indent=2,
        ensure_ascii=False,
    )

    prompt = f"""
You are Jarvis, a personal AI intelligence assistant.

The user asked:
{user_query}

You have been given recent news/article context below.

Articles:
{article_context}

Instructions:
- Use only the provided article context.
- Prioritize articles with full content available.
- Separate confirmed updates from weak/limited context.
- Mention the main themes.
- Do not invent facts, quotes, numbers, dates, or events.
- If sources appear repetitive, merge them into one point.
- Keep the answer clear and conversational.
- End with a short "Main takeaway" sentence.
"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    return response.text or "I could not generate a summary."

def answer_general_question(user_query: str) -> str:
    if not settings.GEMINI_API_KEY:
        return "Gemini API key is missing. Please add GEMINI_API_KEY in your .env file."

    prompt = f"""
You are Jarvis, a personal AI assistant.

Answer the user's question clearly.

User question:
{user_query}

Instructions:
- Be helpful and concise.
- Do not pretend to have real-time information unless sources are provided.
- If the user asks for current information, say that live retrieval is needed.
"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    return response.text or "I could not generate an answer."

def answer_with_hybrid_context(
    user_query: str,
    live_articles: List[Dict],
    stored_chunks: List[Dict],
):
    if not settings.GEMINI_API_KEY:
        return (
            "Gemini API key is missing. "
            "Please add GEMINI_API_KEY to your .env file."
        )

    live_context = []

    for index, article in enumerate(live_articles, start=1):
        live_context.append(
            {
                "reference": f"Live Source {index}",
                "title": article.get("title"),
                "published": article.get("published"),
                "source": article.get("source"),
                "url": article.get("url"),
                "content": (
                    article.get("content")
                    or article.get("summary")
                    or article.get("title")
                ),
            }
        )

    stored_context = []

    for index, result in enumerate(stored_chunks, start=1):
        payload = result.get("payload", {})

        stored_context.append(
            {
                "reference": f"Stored Source {index}",
                "title": payload.get("title"),
                "published": payload.get("published"),
                "source": payload.get("source"),
                "url": payload.get("url"),
                "content_quality": payload.get("content_quality"),
                "text": payload.get("text"),
            }
        )

    prompt = f"""
You are Jarvis, a personal AI intelligence assistant.

The user asked:
{user_query}

You have two types of information:

LIVE NEWS:
{json.dumps(live_context, indent=2, ensure_ascii=False)}

STORED KNOWLEDGE:
{json.dumps(stored_context, indent=2, ensure_ascii=False)}

Instructions:
- Use only the supplied information.
- Clearly separate fresh updates from earlier stored context.
- Compare current developments with earlier patterns when relevant.
- Do not invent facts, events, numbers, dates, or quotes.
- Mention uncertainty if the available context is limited.
- Cite live context as [Live Source X].
- Cite stored context as [Stored Source X].
- Keep the answer conversational.
- End with a short "Main takeaway" sentence.
"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    return response.text or "I could not generate a response."