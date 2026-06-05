from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.schemas.jarvis_schema import (
    UnifiedJarvisResponse,
    UnifiedJarvisSource,
)

from app.services.intent_service import detect_intent
from app.services.query_planner import create_query_plan
from app.services.news_service import get_intelligent_news_context
from app.services.rag_service import (
    answer_from_knowledge_base,
    deduplicate_by_article,
)
from app.services.vector_store_service import search_similar_chunks
from app.services.llm_service import (
    answer_general_question,
    answer_with_hybrid_context,
    summarize_news,
)


def handle_unified_query(
    user_query: str,
    db: Session,
):
    intent_result = detect_intent(user_query)

    query_plan = create_query_plan(
        original_query=user_query,
        intent_result=intent_result,
    )

    if query_plan.retrieval_type == "live_news":
        return handle_live_news(
            user_query=user_query,
            query_plan=query_plan,
        )

    if query_plan.retrieval_type == "knowledge_base":
        return handle_knowledge_base(
            user_query=user_query,
            query_plan=query_plan,
        )

    if query_plan.retrieval_type == "hybrid":
        return handle_hybrid(
            user_query=user_query,
            query_plan=query_plan,
        )

    answer = answer_general_question(user_query)

    return UnifiedJarvisResponse(
        query=user_query,
        intent=query_plan.intent,
        retrieval_type="general",
        entity=query_plan.entity,
        time_range=query_plan.time_range,
        answer=answer,
        sources=[],
        metadata={
            "live_articles": 0,
            "stored_chunks": 0,
        },
    )


def handle_live_news(
    user_query: str,
    query_plan,
):
    articles = get_intelligent_news_context(
        query=query_plan.search_query,
        max_results=8,
        max_articles_to_fetch=5,
    )

    answer = summarize_news(
        user_query=user_query,
        articles=articles,
    )

    sources = [
        UnifiedJarvisSource(
            source_type="live_news",
            title=article.get("title", "Untitled"),
            url=article.get("url"),
            published=article.get("published"),
            content_quality=(
                "full_content"
                if article.get("content_available")
                else "snippet_fallback"
            ),
        )
        for article in articles
    ]

    return UnifiedJarvisResponse(
        query=user_query,
        intent=query_plan.intent,
        retrieval_type="live_news",
        entity=query_plan.entity,
        time_range=query_plan.time_range,
        answer=answer,
        sources=sources,
        metadata={
            "search_query": query_plan.search_query,
            "live_articles": len(articles),
            "stored_chunks": 0,
        },
    )


def handle_knowledge_base(
    user_query: str,
    query_plan,
):
    rag_response = answer_from_knowledge_base(
        query=user_query,
        top_k=5,
        min_score=0.20,
    )

    sources = [
        UnifiedJarvisSource(
            source_type="knowledge_base",
            title=source.title,
            url=source.url,
            published=source.published,
            score=source.score,
            content_quality=source.content_quality,
        )
        for source in rag_response.sources
    ]

    return UnifiedJarvisResponse(
        query=user_query,
        intent=query_plan.intent,
        retrieval_type="knowledge_base",
        entity=query_plan.entity,
        time_range=query_plan.time_range,
        answer=rag_response.answer,
        sources=sources,
        metadata={
            **rag_response.metadata,
            "live_articles": 0,
        },
    )


def handle_hybrid(
    user_query: str,
    query_plan,
):
    articles = get_intelligent_news_context(
        query=query_plan.search_query,
        max_results=5,
        max_articles_to_fetch=3,
    )

    raw_stored_chunks = search_similar_chunks(
        query=user_query,
        limit=15,
        min_score=0.20,
    )

    stored_chunks = deduplicate_by_article(
        results=raw_stored_chunks,
        max_articles=5,
    )

    answer = answer_with_hybrid_context(
        user_query=user_query,
        live_articles=articles,
        stored_chunks=stored_chunks,
    )

    sources: List[UnifiedJarvisSource] = []

    for article in articles:
        sources.append(
            UnifiedJarvisSource(
                source_type="live_news",
                title=article.get("title", "Untitled"),
                url=article.get("url"),
                published=article.get("published"),
                content_quality=(
                    "full_content"
                    if article.get("content_available")
                    else "snippet_fallback"
                ),
            )
        )

    for result in stored_chunks:
        payload = result.get("payload", {})

        sources.append(
            UnifiedJarvisSource(
                source_type="knowledge_base",
                title=payload.get("title", "Untitled"),
                url=payload.get("url"),
                published=payload.get("published"),
                score=round(result.get("score", 0.0), 4),
                content_quality=payload.get(
                    "content_quality",
                    "unknown",
                ),
            )
        )

    return UnifiedJarvisResponse(
        query=user_query,
        intent=query_plan.intent,
        retrieval_type="hybrid",
        entity=query_plan.entity,
        time_range=query_plan.time_range,
        answer=answer,
        sources=sources,
        metadata={
            "search_query": query_plan.search_query,
            "live_articles": len(articles),
            "stored_chunks": len(stored_chunks),
        },
    )