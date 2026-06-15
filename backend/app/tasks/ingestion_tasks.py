from typing import Any, Dict

from app.celery_app import celery_app
from app.db.crud import (
    get_tracked_topics,
    mark_topic_ingested,
    save_ingested_articles,
)
from app.db.database import SessionLocal
from app.services.news_service import get_intelligent_news_context
from app.services.vector_store_service import index_article_chunks


@celery_app.task(
    bind=True,
    name="app.tasks.ingestion_tasks.ingest_tracked_topics",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={
        "max_retries": 3,
    },
)
def ingest_tracked_topics(
    self,
) -> Dict[str, Any]:
    db = SessionLocal()

    try:
        topics = get_tracked_topics(
            db=db,
            enabled_only=True,
        )

        topic_results = []
        affected_article_ids = []

        for topic in topics:
            articles = get_intelligent_news_context(
                query=topic.name,
                max_results=8,
                max_articles_to_fetch=5,
            )

            storage_result = save_ingested_articles(
                db=db,
                articles=articles,
            )

            affected_article_ids.extend(
                storage_result["article_ids"]
            )

            mark_topic_ingested(
                db=db,
                topic_id=topic.id,
            )

            topic_results.append(
                {
                    "topic_id": topic.id,
                    "topic": topic.name,
                    "retrieved_articles": len(articles),
                    "created_articles": storage_result["created_articles"],
                    "reused_articles": storage_result["reused_articles"],
                    "total_chunks": storage_result["total_chunks"],
                }
            )

        unique_article_ids = list(set(affected_article_ids))

        indexing_result = index_article_chunks(
            db=db,
            article_ids=unique_article_ids,
        )

        return {
            "status": "completed",
            "tracked_topics": len(topics),
            "affected_articles": len(unique_article_ids),
            "indexed_chunks": indexing_result["indexed_chunks"],
            "topics": topic_results,
        }

    finally:
        db.close()