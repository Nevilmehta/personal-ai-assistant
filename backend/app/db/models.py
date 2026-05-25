from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
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