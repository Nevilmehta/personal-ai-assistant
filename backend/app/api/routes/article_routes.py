from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.crud import (
    backfill_article_chunks,
    get_article_chunks,
    get_articles,
)
from app.db.database import get_db
from app.schemas.jarvis_schema import (
    ArticleChunkHistory,
    ArticleHistory,
)
from app.services.vector_store_service import (
    index_all_article_chunks,
    search_similar_chunks,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Articles"],
)


@router.get(
    "/articles",
    response_model=List[ArticleHistory],
)
def read_articles(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return get_articles(
        db=db,
        limit=limit,
    )


@router.get(
    "/article-chunks",
    response_model=List[ArticleChunkHistory],
)
def read_article_chunks(
    article_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return get_article_chunks(
        db=db,
        article_id=article_id,
        limit=limit,
    )


@router.post("/article-chunks/backfill")
def backfill_chunks(
    db: Session = Depends(get_db),
):
    return backfill_article_chunks(db=db)


@router.post("/vector/index")
def index_vectors(
    db: Session = Depends(get_db),
):
    return index_all_article_chunks(db=db)


@router.get("/vector/search")
def vector_search(
    query: str,
    limit: int = 5,
):
    return {
        "query": query,
        "results": search_similar_chunks(
            query=query,
            limit=limit,
        ),
    }