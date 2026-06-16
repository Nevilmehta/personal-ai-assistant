from typing import Any, Dict, List
import redis
from qdrant_client import QdrantClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.schemas.jarvis_schema import (
    DetailedHealthResponse,
    ServiceHealthStatus
)
from app.services.embedding_service import get_embedding_dimension

def check_postgres(db: Session):
    try:
        db.execute(text("SELECT 1"))

        return ServiceHealthStatus(
            service="postgresql",
            status="healthy",
            details={
                "connection": "ok",
            },
        )

    except Exception as error:
        return ServiceHealthStatus(
            service="postgresql",
            status="unhealthy",
            error=str(error),
        )

def check_redis():
    try:
        redis_client = redis.Redis.from_url(
            settings.CELERY_BROKER_URL,
            socket_connect_timeout=3,
            socket_timeout=3,
        )

        response = redis_client.ping()

        return ServiceHealthStatus(
            service="redis",
            status="healthy" if response else "unhealthy",
            details={
                "broker_url": settings.CELERY_BROKER_URL,
                "ping": response,
            },
        )

    except Exception as error:
        return ServiceHealthStatus(
            service="redis",
            status="unhealthy",
            error=str(error),
        )

def check_qdrant():
    try:
        client = QdrantClient(
            url=settings.QDRANT_URL,
            timeout=5,
        )

        collections = client.get_collections()

        collection_names = [
            collection.name
            for collection in collections.collections
        ]

        return ServiceHealthStatus(
            service="qdrant",
            status="healthy",
            details={
                "url": settings.QDRANT_URL,
                "collections": collection_names,
                "configured_collection": settings.QDRANT_COLLECTION,
                "collection_exists": (
                    settings.QDRANT_COLLECTION in collection_names
                ),
            },
        )

    except Exception as error:
        return ServiceHealthStatus(
            service="qdrant",
            status="unhealthy",
            error=str(error),
        )

def check_gemini_config():
    if not settings.GEMINI_API_KEY:
        return ServiceHealthStatus(
            service="gemini",
            status="unhealthy",
            error="GEMINI_API_KEY is missing.",
        )

    return ServiceHealthStatus(
        service="gemini",
        status="healthy",
        details={
            "model": settings.GEMINI_MODEL,
            "api_key_configured": True,
        },
    )

def check_embedding_model():
    try:
        dimension = get_embedding_dimension()

        return ServiceHealthStatus(
            service="embedding_model",
            status="healthy",
            details={
                "model": settings.EMBEDDING_MODEL,
                "dimension": dimension,
            },
        )

    except Exception as error:
        return ServiceHealthStatus(
            service="embedding_model",
            status="unhealthy",
            error=str(error),
        )

def calculate_overall_status(
    services: List[ServiceHealthStatus],
) -> str:
    unhealthy_services = [
        service
        for service in services
        if service.status != "healthy"
    ]

    if unhealthy_services:
        return "degraded"

    return "healthy"

def get_detailed_health(db: Session):
    services = [
        ServiceHealthStatus(
            service="fastapi",
            status="healthy",
            details={
                "api": "online",
            },
        ),
        check_postgres(db=db),
        check_redis(),
        check_qdrant(),
        check_gemini_config(),
        check_embedding_model(),
    ]

    return DetailedHealthResponse(
        overall_status=calculate_overall_status(services),
        services=services,
        metadata={
            "project": "Jarvis AI System"
        },
    )