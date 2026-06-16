from typing import List

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.db.crud import (
    create_ingestion_run,
    get_ingestion_run_by_id,
    get_ingestion_runs,
    get_tracked_topics,
    update_ingestion_run_task_id,
)
from app.db.database import get_db
from app.schemas.jarvis_schema import (
    IngestionRunResponse,
    TrackedTopicResponse,
)
from app.tasks.ingestion_tasks import ingest_tracked_topics


router = APIRouter(
    prefix="/api/v1/ingestion",
    tags=["Ingestion"],
)


@router.post("/run")
def trigger_ingestion(
    db: Session = Depends(get_db),
):
    ingestion_run = create_ingestion_run(db=db)

    task = ingest_tracked_topics.delay(
        run_id=ingestion_run.id,
    )

    update_ingestion_run_task_id(
        db=db,
        run_id=ingestion_run.id,
        task_id=task.id,
    )

    return {
        "message": "Background ingestion task queued.",
        "task_id": task.id,
        "ingestion_run_id": ingestion_run.id,
    }


@router.get("/status/{task_id}")
def get_ingestion_status(task_id: str):
    task_result = AsyncResult(
        task_id,
        app=celery_app,
    )

    response = {
        "task_id": task_id,
        "status": task_result.status,
    }

    if task_result.successful():
        response["result"] = task_result.result

    elif task_result.failed():
        response["error"] = str(task_result.result)

    return response


@router.get(
    "/topics",
    response_model=List[TrackedTopicResponse],
)
def get_ingestion_topics(
    db: Session = Depends(get_db),
):
    return get_tracked_topics(
        db=db,
        enabled_only=True,
    )


@router.get(
    "/runs",
    response_model=List[IngestionRunResponse],
)
def list_ingestion_runs(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return get_ingestion_runs(
        db=db,
        limit=limit,
    )


@router.get(
    "/runs/{run_id}",
    response_model=IngestionRunResponse,
)
def read_ingestion_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    run = get_ingestion_run_by_id(
        db=db,
        run_id=run_id,
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Ingestion run not found.",
        )

    return run