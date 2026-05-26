from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class JarvisQuery(Base):
    __tablename__ = "jarvis_queries"

    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(Text, nullable=False)
    intent = Column(String(100), nullable=False)
    entity = Column(String(255), nullable=True)
    time_range = Column(String(100), nullable=True)
    search_query = Column(Text, nullable=True)
    retrieval_type = Column(String(100), nullable=True)

    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sources = relationship(
        "JarvisSource",
        back_populates="query",
        cascade="all, delete-orphan"
    )

    article_links = relationship(
        "QueryArticle",
        cascade="all, delete-orphan"
    )

class JarvisSource(Base):
    __tablename__ = "jarvis_sources"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(
        Integer,
        ForeignKey("jarvis_queries.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    published = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    query = relationship(
        "JarvisQuery",
        back_populates="sources"
    )

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False, unique=True, index=True)
    published = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)

    snippet = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    content_available = Column(Boolean, default=False)

    content_hash = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    query_links = relationship(
        "QueryArticle",
        back_populates="article",
        cascade="all, delete-orphan"
    )

class QueryArticle(Base):
    __tablename__ = "query_articles"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(
        Integer,
        ForeignKey("jarvis_queries.id", ondelete="CASCADE"),
        nullable=False
    )

    article_id = Column(
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    article = relationship("Article", back_populates="query_links")

    __table_args__ = (
        UniqueConstraint("query_id", "article_id", name="uq_query_article"),
    )