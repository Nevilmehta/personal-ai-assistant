from app.schemas.jarvis_schema import (
    JarvisAskResponse,
    NewsSource
)
from app.db.crud import save_jarvis_query

from typing import Optional
from sqlalchemy.orm import Session

from app.services.query_planner import create_query_plan
from app.services.news_service import get_intelligent_news_context
from app.services.llm_service import summarize_news, answer_general_question
from app.services.intent_service import detect_intent

# This is first real Jarvis backend pipeline
def handle_user_query(user_query: str, db: Optional[Session] = None):
    """
    Main Jarvis pipeline.

    Flow:
    1. Detect intent
    2. Create query plan
    3. Retrieve required data
    4. Generate response
    5. Return structured response
    """

    intent_result = detect_intent(user_query)

    query_plan = create_query_plan(
        original_query=user_query, 
        intent_result=intent_result
    )
    
    if query_plan.retrieval_type == "news_search":
        articles = get_intelligent_news_context(
            query=query_plan.search_query,
            max_results=8,
            max_articles_to_fetch=5,
        )

        summary = summarize_news(
            user_query=user_query, 
            articles=articles
        )

        sources = [
            NewsSource(
                title=article["title"],
                url=article["url"],
                published=article.get("published"),
                source=article.get("source"),
            )
            for article in articles
        ]

        if db:
            save_jarvis_query(
                db=db,
                user_query=user_query,
                intent=query_plan.intent,
                entity=query_plan.entity,
                time_range=query_plan.time_range,
                search_query=query_plan.search_query,
                retrieval_type=query_plan.retrieval_type,
                summary=summary,
                sources=articles
            )

        return JarvisAskResponse(
            intent=query_plan.intent,
            entity=query_plan.entity,
            time_range=query_plan.time_range,
            summary=summary,
            sources=sources,
            metadata={
                "search_query": query_plan.search_query,
                "retrieval_type": query_plan.retrieval_type,
                "article_count": len(articles),
                "full_content_articles": sum(
                    1 for article in articles if article.get("content_available")
                ),
                "saved_to_history": db is not None
            },
        )

    summary = answer_general_question(user_query)

    if db:
        save_jarvis_query(
            db=db,
            user_query=user_query,
            intent=query_plan.intent,
            entity=query_plan.entity,
            time_range=query_plan.time_range,
            search_query=query_plan.search_query,
            retrieval_type=query_plan.retrieval_type,
            summary=summary,
            sources=[]
        )

    return JarvisAskResponse(
        intent=query_plan.intent,
        entity=query_plan.entity,
        time_range=query_plan.time_range,
        summary=summary,
        sources=[],
        metadata={
            "search_query": query_plan.search_query,
            "retrieval_type": query_plan.retrieval_type,
            "article_count": 0,
            "saved_to_history": db is not None
        },
    )
