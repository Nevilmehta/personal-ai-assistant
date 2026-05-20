from fastapi import FastAPI, HTTPException

from app.schemas.jarvis_schema import (
    JarvisAskRequest,
    JarvisAskResponse,
    NewsSource
)
from app.services.intent_service import detect_intent
from app.services.news_service import search_news
from app.services.llm_service import summarize_news

app = FastAPI(title="Jarvis - Personal AI Intelligence Platform",
            description="Personal AI Intelligence System - Phase 1",
            version="0.1.0")

@app.get("/")
def root():
    return {
        "message": "Jarvis AI System is running.",
        "phase": "Phase 1 - Core Backend",
    }

@app.post("/api/v1/jarvis/ask", response_model=JarvisAskResponse)
def ask_jarvis(request: JarvisAskRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    intent_data = detect_intent(request.query)

    entity = intent_data.get("entity")
    intent = intent_data.get("intent")
    time_range = intent_data.get("time_range")

    if intent == "latest_news":
        search_query = entity or request.query
        articles = search_news(search_query)
        summary = summarize_news(request.query, articles)

        sources = [
            NewsSource(
                title=article["title"],
                url=article["url"],
                published=article.get("published"),
                source=article.get("source")
            )
            for article in articles
        ]

        return JarvisAskResponse(
            intent=intent,
            entity=entity,
            time_range=time_range,
            summary=summary,
            sources=sources
        )

    summary = summarize_news(request.query, [])

    return JarvisAskResponse(
        intent=intent,
        entity=entity,
        time_range=time_range,
        summary=summary,
        sources=[]
    )