import hashlib
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from app.db.models import Article, ArticleChunk, JarvisQuery, JarvisSource, QueryArticle, TrackedTopic
from app.services.chunking_service import chunk_text, generate_text_hash
from datetime import datetime, timezone
from typing import List, Dict, Optional

QUALITY_RANK = {
    "title_fallback": 1,
    "snippet_fallback": 2,
    "full_content": 3,
}

def select_article_text(article: Article) -> tuple[str, str]:
    if article.content:
        return article.content, "full_content"

    if article.snippet:
        return article.snippet, "snippet_fallback"

    return article.title, "title_fallback"

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

        article = get_or_create_article(db=db, article_data=source)
        query_article_link = QueryArticle(query_id = query_record.id, article_id = article.id)

        db.add(query_article_link)

        save_article_chunks(db=db, article=article)

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

def generate_content_hash(text: Optional[str]):
    if not text:
        return None
    
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_or_create_article(
    db: Session,
    article_data: Dict
):
    url = article_data.get("url", "")
    existing_article = db.query(Article).filter(Article.url == url).first()

    content = article_data.get("content")

    if existing_article:
        if content and not existing_article.content:
            existing_article.content = content
            existing_article.content_available = article_data.get("content_available", False)
            existing_article.content_hash = generate_content_hash(content)

        return existing_article

    article = Article(
        title=article_data.get("title", "Untitled"),
        url=url,
        published=article_data.get("published"),
        source=article_data.get("source"),
        snippet=article_data.get("summary"),
        content=content,
        content_available=article_data.get("content_available", False),
        content_hash=generate_content_hash(content),
    )

    db.add(article)
    db.flush()
    return article

def get_articles(db: Session, limit: int = 20):
    return db.query(Article).order_by(Article.created_at.desc()).limit(limit).all()

def save_article_chunks(
    db: Session,
    article: Article,
    chunk_size: int = 700,
    overlap: int = 100,
):
    text_to_chunk, content_quality = select_article_text(article)

    if not text_to_chunk:
        return 0

    existing_chunks = (
        db.query(ArticleChunk)
        .filter(ArticleChunk.article_id == article.id)
        .all()
    )

    if existing_chunks:
        existing_quality = existing_chunks[0].content_quality

        if QUALITY_RANK[existing_quality] >= QUALITY_RANK[content_quality]:
            return len(existing_chunks)

        for chunk in existing_chunks:
            db.delete(chunk)

        db.flush()

    chunks = chunk_text(
        text=text_to_chunk,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    for index, chunk in enumerate(chunks):
        db.add(
            ArticleChunk(
                article_id=article.id,
                chunk_index=index,
                content=chunk,
                content_hash=generate_text_hash(chunk),
                content_quality=content_quality,
            )
        )

    db.flush()

    return len(chunks)

def backfill_article_chunks(db: Session):
    articles = db.query(Article).all()

    processed_articles = 0
    total_chunks = 0

    for article in articles:
        chunk_count = save_article_chunks(
            db=db,
            article=article
        )

        processed_articles += 1
        total_chunks += chunk_count

    db.commit()

    return {
        "processed_articles": processed_articles,
        "total_chunks": total_chunks
    }

def get_article_chunks(db: Session, article_id: int|None=None, limit: int = 20):
    query = db.query(ArticleChunk)
    if article_id is not None:
        query = query.filter(ArticleChunk.article_id == article_id)

    return (
        query.order_by(ArticleChunk.created_at.desc()).limit(limit).all()
    )

def save_ingested_articles(db: Session, articles: List[Dict[str, Any]]):
    """
    Stores articles discovered by the scheduled ingestion worker.

    Existing articles are reused and upgraded when better content
    becomes available.
    """
    created_articles = 0
    reused_articles = 0
    total_chunks = 0
    article_ids = []

    for article_data in articles:
        url = article_data.get("url")

        if not url:
            continue

        existing_article = (
            db.query(Article)
            .filter(Article.url == url)
            .first()
        )

        if existing_article:
            article = existing_article
            reused_articles += 1

            article.title = (
                article_data.get("title")
                or article.title
            )

            article.published = (
                article_data.get("published")
                or article.published
            )

            article.source = (
                article_data.get("source")
                or article.source
            )

            article.snippet = (
                article_data.get("summary")
                or article.snippet
            )

            incoming_content = article_data.get("content")

            if incoming_content and (
                not article.content
                or len(incoming_content) > len(article.content)
            ):
                article.content = incoming_content
                article.content_available = True
                article.content_hash = generate_content_hash(
                    incoming_content
                )

        else:
            article = get_or_create_article(
                db=db,
                article_data=article_data,
            )

            created_articles += 1

        db.flush()

        chunk_count = save_article_chunks(
            db=db,
            article=article,
        )

        total_chunks += chunk_count
        article_ids.append(article.id)

    db.commit()

    return {
        "created_articles": created_articles,
        "reused_articles": reused_articles,
        "total_chunks": total_chunks,
        "article_ids": list(set(article_ids)),
    }

def create_tracked_topic(
    db: Session,
    name: str,
    description: Optional[str] = None,
    enabled: bool = True,
    ingestion_interval_minutes: int = 30
):
    existing_topic = (
        db.query(TrackedTopic)
        .filter(TrackedTopic.name == name)
        .first()
    )

    if existing_topic:
        return existing_topic

    topic = TrackedTopic(
        name=name,
        description=description,
        enabled=enabled,
        ingestion_interval_minutes=ingestion_interval_minutes
    )

    db.add(topic)
    db.commit()
    db.refresh(topic)

    return topic

def get_tracked_topics(db: Session, enabled_only: bool = False):
    query = db.query(TrackedTopic)
    if enabled_only:
        query = query.filter(TrackedTopic.enabled == True)

    return query.order_by(TrackedTopic.created_at.desc()).all()

def get_tracked_topic_by_id(db: Session, topic_id: int):
    return (
        db.query(TrackedTopic)
        .filter(TrackedTopic.id == topic_id)
        .first()
    )

def update_tracked_topic(
    db: Session,
    topic_id: int,
    update_data: dict
):
    topic = get_tracked_topic_by_id(
        db=db,
        topic_id=topic_id,
    )

    if not topic:
        return None

    for field, value in update_data.items():
        if value is not None:
            setattr(topic, field, value)

    db.commit()
    db.refresh(topic)

    return topic

def delete_tracked_topic(db: Session, topic_id: int):
    topic = get_tracked_topic_by_id(
        db=db,
        topic_id=topic_id,
    )

    if not topic:
        return False

    db.delete(topic)
    db.commit()

    return True

def seed_default_topics(db: Session):
    default_topics = [
        "artificial intelligence",
        "AI startups",
        "OpenAI",
        "Anthropic",
        "NVIDIA AI",
    ]

    created_count = 0

    for topic_name in default_topics:
        existing_topic = (
            db.query(TrackedTopic)
            .filter(TrackedTopic.name == topic_name)
            .first()
        )

        if existing_topic:
            continue

        topic = TrackedTopic(
            name=topic_name,
            enabled=True,
            ingestion_interval_minutes=30,
        )

        db.add(topic)
        created_count += 1

    db.commit()

    return created_count

def mark_topic_ingested(
    db: Session,
    topic_id: int
):
    topic = get_tracked_topic_by_id(
        db = db,
        topic_id= topic_id
    )

    if not topic:
        return None

    topic.last_ingested_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(topic)

    return topic