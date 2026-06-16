from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.crud import (
    get_ingestion_dashboard_summary,
    get_knowledge_base_summary,
    get_topic_dashboard_summary,
)
from app.db.database import get_db
from app.schemas.jarvis_schema import (
    IngestionDashboardSummary,
    TrackedTopicResponse,
)
from app.services.health_service import get_detailed_health


router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/ingestion",
    response_model=IngestionDashboardSummary,
)
def read_ingestion_dashboard(
    db: Session = Depends(get_db),
):
    return get_ingestion_dashboard_summary(db=db)


@router.get(
    "/topics",
    response_model=List[TrackedTopicResponse],
)
def read_topics_dashboard(
    db: Session = Depends(get_db),
):
    return get_topic_dashboard_summary(db=db)


@router.get("/knowledge-base")
def read_knowledge_base_dashboard(
    db: Session = Depends(get_db),
):
    return get_knowledge_base_summary(db=db)


@router.get("/system")
def read_system_dashboard(
    db: Session = Depends(get_db),
):
    return get_detailed_health(db=db)