from typing import Any, Dict, Optional

from app.celery_app import celery_app
from app.db.crud import (
    add_ingestion_topic_run,
    complete_ingestion_run,
    create_ingestion_run,
    fail_ingestion_run,
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
    run_id: Optional[int] = None,
) -> Dict[str, Any]:
    db = SessionLocal()

    active_run_id = run_id

    try:
        if active_run_id is None:
            ingestion_run = create_ingestion_run(
                db=db,
                task_id=self.request.id,
            )
            active_run_id = ingestion_run.id

        topics = get_tracked_topics(
            db=db,
            enabled_only=True,
        )

        topic_results = []
        affected_article_ids = []

        total_articles_retrieved = 0
        total_articles_created = 0
        total_articles_reused = 0
        total_chunks = 0

        for topic in topics:
            try:
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

                retrieved_count = len(articles)
                created_count = storage_result["created_articles"]
                reused_count = storage_result["reused_articles"]
                chunk_count = storage_result["total_chunks"]

                total_articles_retrieved += retrieved_count
                total_articles_created += created_count
                total_articles_reused += reused_count
                total_chunks += chunk_count

                mark_topic_ingested(
                    db=db,
                    topic_id=topic.id,
                )

                add_ingestion_topic_run(
                    db=db,
                    ingestion_run_id=active_run_id,
                    topic_id=topic.id,
                    topic_name=topic.name,
                    retrieved_articles=retrieved_count,
                    created_articles=created_count,
                    reused_articles=reused_count,
                    chunks_created=chunk_count,
                    status="success",
                )

                topic_results.append(
                    {
                        "topic_id": topic.id,
                        "topic": topic.name,
                        "retrieved_articles": retrieved_count,
                        "created_articles": created_count,
                        "reused_articles": reused_count,
                        "total_chunks": chunk_count,
                        "status": "success",
                    }
                )

            except Exception as topic_error:
                add_ingestion_topic_run(
                    db=db,
                    ingestion_run_id=active_run_id,
                    topic_id=topic.id,
                    topic_name=topic.name,
                    retrieved_articles=0,
                    created_articles=0,
                    reused_articles=0,
                    chunks_created=0,
                    status="failed",
                    error_message=str(topic_error),
                )

                topic_results.append(
                    {
                        "topic_id": topic.id,
                        "topic": topic.name,
                        "status": "failed",
                        "error": str(topic_error),
                    }
                )

        unique_article_ids = list(set(affected_article_ids))

        indexing_result = index_article_chunks(
            db=db,
            article_ids=unique_article_ids,
        )

        total_indexed_chunks = indexing_result["indexed_chunks"]

        complete_ingestion_run(
            db=db,
            run_id=active_run_id,
            total_topics=len(topics),
            total_articles_retrieved=total_articles_retrieved,
            total_articles_created=total_articles_created,
            total_articles_reused=total_articles_reused,
            total_chunks=total_chunks,
            total_indexed_chunks=total_indexed_chunks,
        )

        return {
            "status": "completed",
            "ingestion_run_id": active_run_id,
            "tracked_topics": len(topics),
            "affected_articles": len(unique_article_ids),
            "indexed_chunks": total_indexed_chunks,
            "topics": topic_results,
        }

    except Exception as error:
        if active_run_id is not None:
            fail_ingestion_run(
                db=db,
                run_id=active_run_id,
                error_message=str(error),
            )

        raise

    finally:
        db.close()