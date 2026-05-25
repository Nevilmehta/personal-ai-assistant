from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.crud import get_jarvis_history
from app.db.database import Base, engine, get_db
from app.schemas.jarvis_schema import (
    JarvisAskRequest,
    JarvisAskResponse,
    JarvisQueryHistory
)
from app.services.jarvis_orchestrator import handle_user_query

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