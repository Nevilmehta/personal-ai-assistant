from fastapi import APIRouter, HTTPException

from app.schemas.jarvis_schema import RAGAskRequest, RAGAskResponse
from app.services.rag_service import answer_from_knowledge_base


router = APIRouter(
    prefix="/api/v1/rag",
    tags=["RAG"],
)


@router.post("/ask", response_model=RAGAskResponse)
def ask_rag(request: RAGAskRequest):
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    return answer_from_knowledge_base(
        query=request.query,
        top_k=request.top_k,
        min_score=request.min_score,
    )