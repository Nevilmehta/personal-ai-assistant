from datetime import timedelta
from celery import Celery
from app.config import settings

celery_app = Celery(
    "jarvis",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.ingestion_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone=settings.JARVIS_TIMEZONE,
    enable_utc=True,

    task_routes={
        "app.tasks.ingestion_tasks.*": {"queue": "ingestion"},
    },

    beat_schedule={
        "ingest-tracked-topics-periodically": {
            "task": (
                "app.tasks.ingestion_tasks."
                "ingest_tracked_topics"
            ),
            "schedule": timedelta(minutes= settings.INGESTION_INTERVAL_MINUTES),  
        },
    },
)
