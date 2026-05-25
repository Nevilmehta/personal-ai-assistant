from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.db.models import JarvisQuery, JarvisSource

def save_jarvis_query(
    db: Session,
    user_query: str,
    intent: str,
    entity: Optional[str],
    time_range: Optional[str],
    search_query: Optional[str],
    retrieval_type: Optional[str],
    summary: Optional[str],
    sources: List[Dict]
):
    query_record = JarvisQuery(
        user_query=user_query,
        intent=intent,
        entity=entity,
        time_range=time_range,
        search_query=search_query,
        retrieval_type=retrieval_type,
        summary=summary
    )

    db.add(query_record)
    db.flush()

    for source in sources:
        source_record = JarvisSource(
            query_id = query_record.id,
            title = source.get("title", "untitled"),
            url = source.get("url", ""),
            published = source.get("published"),
            source = source.get("source")
        )
        db.add(source_record)

    db.commit()
    db.refresh(query_record)
    return query_record

def get_jarvis_history(
    db: Session,
    limit: int = 20
):
    return (
        db.query(JarvisQuery)
        .order_by(JarvisQuery.created_at.desc())
        .limit(limit)
        .all()
    )