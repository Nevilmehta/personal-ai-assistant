from fastapi import FastAPI, HTTPException
from app.schemas.jarvis_schema import (
    JarvisAskRequest,
    JarvisAskResponse
)
from app.services.jarvis_orchestrator import handle_user_query

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
def ask_jarvis(request: JarvisAskRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    return handle_user_query(request.query)