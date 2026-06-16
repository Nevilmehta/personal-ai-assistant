from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.jarvis_schema import DetailedHealthResponse
from app.services.health_service import get_detailed_health


router = APIRouter(
    tags=["Health"],
)


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


@router.get(
    "/api/v1/health/detailed",
    response_model=DetailedHealthResponse,
)
def read_detailed_health(
    db: Session = Depends(get_db),
):
    return get_detailed_health(db=db)