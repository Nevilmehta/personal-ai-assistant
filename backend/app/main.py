from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.crud import get_jarvis_history, get_articles, get_article_chunks, backfill_article_chunks
from app.db.database import Base, engine, get_db
from app.schemas.jarvis_schema import (
    ArticleChunkHistory,
    ArticleHistory,
    JarvisAskRequest,
    JarvisAskResponse,
    JarvisQueryHistory
)
from app.services.jarvis_orchestrator import handle_user_query
from app.services.vector_store_service import index_all_article_chunks, search_similar_chunks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jarvis - Personal AI Intelligence Platform",
            description="Personal AI Intelligence System - Phase 1",
            version="0.1.1")

@app.get("/")
def root():
    return {
        "message": "Jarvis AI System is running.",
        "phase": "Phase 1 - Core Backend",
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }

@app.post("/api/v1/jarvis/ask", response_model=JarvisAskResponse)
def ask_jarvis(request: JarvisAskRequest, db: Session = Depends(get_db)):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    return handle_user_query(user_query=request.query, db=db)

@app.get("/api/v1/jarvis/history", response_model=List[JarvisQueryHistory])
def read_jarvis_history(limit: int = 20, db: Session = Depends(get_db)):
    history_records = get_jarvis_history(db=db, limit=limit)
    return history_records

@app.get("/api/v1/articles", response_model=List[ArticleHistory])
def read_articles(limit: int = 20, db: Session = Depends(get_db)):
    return get_articles(db=db, limit=limit)

@app.get("/api/v1/article_chunks", response_model=List[ArticleChunkHistory])
def read_article_chunks(article_id: int | None = None, limit: int = 50, db: Session = Depends(get_db)):
    return get_article_chunks(db=db, article_id=article_id, limit=limit)

@app.post("/api/v1/article-chunks/backfill")
def backfill_chunks(db: Session = Depends(get_db)):
    return backfill_article_chunks(db=db)

@app.post("/api/v1/vector/index")
def index_vectors(db: Session = Depends(get_db)):
    return index_all_article_chunks(db=db)

@app.get("/api/v1/vector/search")
def vector_search(query: str,limit: int = 5):
    return {
        "query": query,
        "results": search_similar_chunks(query=query, limit=limit)
    }