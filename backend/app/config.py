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
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

settings = Settings()