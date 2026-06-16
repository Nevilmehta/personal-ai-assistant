import os 
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/jarvis_db",
    )

    QDRANT_URL: str = os.getenv(
        "QDRANT_URL",
        "http://localhost:6333",
    )
    QDRANT_COLLECTION: str = os.getenv(
        "QDRANT_COLLECTION",
        "jarvis_article_chunks"
    )
    QDRANT_GRPC_HOST: str = os.getenv(
        "QDRANT_GRPC_HOST",
        "127.0.0.1",
    )

    QDRANT_GRPC_PORT: int = int(
        os.getenv("QDRANT_GRPC_PORT", "6334")
    )

    QDRANT_USE_GRPC: bool = os.getenv(
        "QDRANT_USE_GRPC",
        "true",
    ).lower() == "true"

    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    CELERY_BROKER_URL: str = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:6379/0",
    )
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/1",
    )
    TRACKED_NEWS_TOPICS: list[str] = [
        topic.strip()
        for topic in os.getenv(
            "TRACKED_NEWS_TOPICS",
            "artificial intelligence,AI startups,OpenAI,Anthropic,NVIDIA AI",
        ).split(",")
        if topic.strip()
    ]
    INGESTION_INTERVAL_MINUTES: int = int(
        os.getenv("INGESTION_INTERVAL_MINUTES", "30")
    )
    JARVIS_TIMEZONE: str = os.getenv("JARVIS_TIMEZONE", "Asia/Kolkata")

settings = Settings()