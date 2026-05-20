import json
from typing import List, Dict
from google import genai
from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def summarize_news(user_query: str, articles: List[Dict]):
    if not settings.GEMINI_API_KEY:
        return "Gemini API key is missing. Please add GEMINI_API_KEY in your .env file."

    if not articles:
        return "I could not find recent news for this query."

    article_context = json.dumps(articles, indent=2, ensure_ascii=False)

    prompt = f"""
You are Jarvis, a personal AI intelligence assistant.

The user asked:
{user_query}

Use the following news articles to answer clearly and concisely.

Articles:
{article_context}

Instructions:
- Summarize the most important updates.
- Mention uncertainty if the articles do not provide enough detail.
- Do not make up facts.
- Keep the answer useful and conversational.
- Avoid saying "as an AI model".
"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt
    )

    return response.text or "I could not generate a summary."