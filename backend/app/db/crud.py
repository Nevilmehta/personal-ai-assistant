import hashlib
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.db.models import Article, JarvisQuery, JarvisSource, QueryArticle

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