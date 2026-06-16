from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.crud import (
    create_tracked_topic,
    delete_tracked_topic,
    get_tracked_topics,
    seed_default_topics,
    update_tracked_topic,
)
from app.db.database import get_db
from app.schemas.jarvis_schema import (
    TrackedTopicCreate,
    TrackedTopicResponse,
    TrackedTopicUpdate,
)


router = APIRouter(
    prefix="/api/v1/topics",
    tags=["Topics"],
)


@router.post(
    "",
    response_model=TrackedTopicResponse,
)
def create_topic(
    request: TrackedTopicCreate,
    db: Session = Depends(get_db),
):
    if not request.name.strip():
        raise HTTPException(
            status_code=400,
            detail="Topic name cannot be empty.",
        )

    return create_tracked_topic(
        db=db,
        name=request.name.strip(),
        description=request.description,
        enabled=request.enabled,
        ingestion_interval_minutes=request.ingestion_interval_minutes,
    )


@router.get(
    "",
    response_model=List[TrackedTopicResponse],
)
def list_topics(
    enabled_only: bool = False,
    db: Session = Depends(get_db),
):
    return get_tracked_topics(
        db=db,
        enabled_only=enabled_only,
    )


@router.patch(
    "/{topic_id}",
    response_model=TrackedTopicResponse,
)
def update_topic(
    topic_id: int,
    request: TrackedTopicUpdate,
    db: Session = Depends(get_db),
):
    topic = update_tracked_topic(
        db=db,
        topic_id=topic_id,
        update_data=request.model_dump(exclude_unset=True),
    )

    if not topic:
        raise HTTPException(
            status_code=404,
            detail="Topic not found.",
        )

    return topic


@router.delete("/{topic_id}")
def remove_topic(
    topic_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_tracked_topic(
        db=db,
        topic_id=topic_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Topic not found.",
        )

    return {
        "message": "Topic deleted successfully.",
        "topic_id": topic_id,
    }


@router.post("/seed-defaults")
def seed_topics(
    db: Session = Depends(get_db),
):
    created_count = seed_default_topics(db=db)

    return {
        "message": "Default topics seeded.",
        "created_count": created_count,
    }