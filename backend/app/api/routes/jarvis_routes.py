from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.jarvis_schema import (
    JarvisAskRequest,
    JarvisAskResponse,
    UnifiedJarvisResponse,
)
from app.services.jarvis_orchestrator import handle_user_query
from app.services.unified_jarvis_service import handle_unified_query


router = APIRouter(
    prefix="/api/v1/jarvis",
    tags=["Jarvis"],
)


@router.post("/ask", response_model=JarvisAskResponse)
def ask_jarvis(
    request: JarvisAskRequest,
    db: Session = Depends(get_db),
):
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    return handle_user_query(
        user_query=request.query,
        db=db,
    )


@router.post("/unified-ask", response_model=UnifiedJarvisResponse)
def ask_unified_jarvis(
    request: JarvisAskRequest,
    db: Session = Depends(get_db),
):
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    return handle_unified_query(
        user_query=request.query,
        db=db,
    )