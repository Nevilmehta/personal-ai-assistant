import json
from typing import List, Dict

from google import genai

from app.config import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def summarize_news(user_query: str, articles: List[Dict]) -> str:
    if not settings.GEMINI_API_KEY:
        return "Gemini API key is missing. Please add GEMINI_API_KEY in your .env file."

    if not articles:
        return "I could not find recent news for this query."

    article_context = json.dumps(articles, indent=2, ensure_ascii=False)

    prompt = f"""
You are Jarvis, a personal AI intelligence assistant.

The user asked:
{user_query}

Use only the following news article data to answer.

Articles:
{article_context}

Instructions:
- Give a clear summary of the most important updates.
- Group related updates together.
- Mention if available information is limited.
- Do not make up facts.
- Do not invent dates, numbers, quotes, or events.
- Keep the tone natural, like a helpful personal assistant.
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