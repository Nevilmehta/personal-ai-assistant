from typing import Any, Dict, List
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams
)
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.db.models import ArticleChunk
from app.services.embedding_service import (
    embed_text,
    get_embedding_dimension,
    embed_texts
)

client = QdrantClient(url=settings.QDRANT_URL)

def ensure_collection_exists():
    if client.collection_exists(settings.QDRANT_COLLECTION):
        return

    client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=get_embedding_dimension(),
            distance=Distance.COSINE
        )
    )

def index_all_article_chunks(db: Session):
    ensure_collection_exists()

    chunks = (db.query(ArticleChunk)
        .options(joinedload(ArticleChunk.article))
        .all()
    )

    if not chunks:
        return {
            "indexed_chunks": 0
        }

    vectors = embed_texts([chunk.content for chunk in chunks])

    points = []

    for chunk, vector in zip(chunks, vectors):
        article = chunk.article

        points.append(
            PointStruct(
                id=chunk.id,
                vector=vector,
                payload={
                    "chunk_id": chunk.id,
                    "article_id": article.id,
                    "chunk_index": chunk.chunk_index,
                    "title": article.title,
                    "source": article.source,
                    "published": article.published,
                    "url": article.url,
                    "content_quality": chunk.content_quality,
                    "text": chunk.content,
                },
            )
        )

    client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        wait=True,
        points=points
    )

    return {
        "indexed_chunks": len(points)
    }

def search_similar_chunks(query: str, limit: int = 5):
    ensure_collection_exists()

    query_vector = embed_text(query)

    results = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=limit,
        with_payload=True
    ).points

    return [
        {
            "score": result.score,
            "payload": result.payload
        }
        for result in results
    ]