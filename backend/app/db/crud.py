import hashlib
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.db.models import Article, ArticleChunk, JarvisQuery, JarvisSource, QueryArticle
from app.services.chunking_service import chunk_text, generate_text_hash

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

def save_article_chunks(db: Session, article: Article, chunk_size: int = 1000, overlap: int = 150):
    if not article.content:
        return 0

    existing_count = db.query(ArticleChunk).filter(ArticleChunk.article_id == article.id).count()

    if existing_count > 0:
        return existing_count

    chunks = chunk_text(article.content, chunk_size=chunk_size, overlap=overlap)
    for index, chunk in enumerate(chunks):
        chunk_record = ArticleChunk(
            article_id=article.id,
            chunk_index=index,
            content=chunk,
            content_hash=generate_text_hash(chunk)
        )
        db.add(chunk_record)

    db.flush()

    return len(chunks)

def get_article_chunks(db: Session, article_id: int|None=None, limit: int = 20):
    query = db.query(ArticleChunk)
    if article_id is not None:
        query = query.filter(ArticleChunk.article_id == article_id)

    return (
        query.order_by(ArticleChunk.created_at.desc()).limit(limit).all()
    )
