from typing import Any, Dict, List, Optional
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

client = QdrantClient(
    host=settings.QDRANT_GRPC_HOST,
    grpc_port=settings.QDRANT_GRPC_PORT,
    prefer_grpc=settings.QDRANT_USE_GRPC,
    timeout=30,
)

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

def index_article_chunks(
    db: Session,
    article_ids: Optional[List[int]] = None,
) -> Dict[str, int]:
    """
    Indexes article chunks into Qdrant.

    If article_ids are supplied, only chunks belonging to those
    articles are indexed.
    """

    ensure_collection_exists()

    query = (
        db.query(ArticleChunk)
        .options(joinedload(ArticleChunk.article))
    )

    if article_ids:
        query = query.filter(
            ArticleChunk.article_id.in_(article_ids)
        )

    chunks = query.all()

    if not chunks:
        return {
            "indexed_chunks": 0,
        }

    vectors = embed_texts(
        [chunk.content for chunk in chunks]
    )

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
        points=points,
    )

    return {
        "indexed_chunks": len(points),
    }


def index_all_article_chunks(
    db: Session,
) -> Dict[str, int]:
    return index_article_chunks(
        db=db,
        article_ids=None,
    )

def search_similar_chunks(query: str, limit: int = 10, min_score: float = 0.0):
    ensure_collection_exists()

    query_vector = embed_text(query)

    results = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=limit,
        with_payload=True
    ).points

    matches = []

    for result in results:
        if result.score < min_score:
            continue

        matches.append({
            "score": result.score,
            "payload": result.payload
        })

    return matches