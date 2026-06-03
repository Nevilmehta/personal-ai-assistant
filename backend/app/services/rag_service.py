from typing import List, Dict, Any
from app.schemas.jarvis_schema import RAGAskRequest, RAGAskResponse, RAGSource

from app.services.llm_service import answer_with_rag_context
from app.services.vector_store_service import search_similar_chunks

def deduplicate_by_article(results: List[Dict[str, any]], max_articles: int):
    """
    Avoids returning several chunks from the same article.

    Results arrive in similarity-score order, so the first matching
    chunk for an article is kept.
    """

    seen_article_ids = set()
    unique_results = []

    for result in results:
        payload = result.get("payload", {})
        article_id = payload.get("article_id")

        if article_id is None:
            continue

        if article_id in seen_article_ids:
            continue

        seen_article_ids.add(article_id)
        unique_results.append(result)

        if len(unique_results) >= max_articles:
            break

    return unique_results

def answer_from_knowledge_base(
    query: str,
    top_k: int = 5,
    min_score: float = 0.20,
):
    """
    Main RAG pipeline:

    1. Vector-search stored chunks
    2. Remove repetitive articles
    3. Send context to LLM
    4. Return grounded answer and sources
    """

    raw_results = search_similar_chunks(
        query=query,
        limit=top_k * 3,
        min_score=min_score,
    )

    selected_results = deduplicate_by_article(
        results=raw_results,
        max_articles=top_k,
    )

    answer = answer_with_rag_context(
        user_query=query,
        retrieved_chunks=selected_results,
    )

    sources = []

    for result in selected_results:
        payload = result.get("payload", {})

        sources.append(
            RAGSource(
                article_id=payload.get("article_id"),
                chunk_id=payload.get("chunk_id"),
                title=payload.get("title", "Untitled"),
                url=payload.get("url"),
                source=payload.get("source"),
                published=payload.get("published"),
                score=round(result.get("score", 0.0), 4),
                content_quality=payload.get("content_quality", "unknown"),
            )
        )

    return RAGAskResponse(
        query=query,
        answer=answer,
        sources=sources,
        metadata={
            "retrieval_type": "qdrant_semantic_search",
            "raw_matches": len(raw_results),
            "selected_sources": len(selected_results),
            "top_k": top_k,
            "min_score": min_score,
        }
    )
