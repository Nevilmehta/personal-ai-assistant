from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any

class RAGAskRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    min_score: float = Field(default=0.20, ge=0.0, le=1.0)

class RAGSource(BaseModel):
    article_id: int
    chunk_id: int 
    title: str
    url: Optional[str] = None
    source: Optional[str] = None
    published: Optional[str] = None
    score: float
    content_quality: str

class RAGAskResponse(BaseModel):
    query: str
    answer: str
    sources: List[RAGSource]
    metadata: Dict[str, Any] 

class JarvisAskRequest(BaseModel):
    query: str
    mode: Optional[str] = "auto"

class IntentResult(BaseModel):
    intent: str
    entity: Optional[str] = None
    time_range: Optional[str] = None

class QueryPlan(BaseModel):
    original_query: str
    intent: str
    entity: Optional[str] = None
    time_range: Optional[str] = None
    search_query: str
    retrieval_type: str

class NewsSource(BaseModel):
    title: str
    url: str
    published: Optional[str] = None
    source: Optional[str] = None

class JarvisAskResponse(BaseModel):
    intent: str
    entity: Optional[str] = None
    time_range: Optional[str] = None
    summary: str
    sources: List[NewsSource] 
    metadata: Optional[Dict[str, Any]] = None

class JarvisSourceHistory(BaseModel):
    title: str
    url: str
    published: Optional[str] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True

class JarvisQueryHistory(BaseModel):
    id: int
    user_query: str
    intent: str
    entity: Optional[str] = None
    time_range: Optional[str] = None
    search_query: Optional[str] = None
    retrieval_type: Optional[str] = None
    summary: str
    created_at: datetime
    sources: List[JarvisSourceHistory] = []

    class Config:
        from_attributes = True

class ArticleHistory(BaseModel):
    id: int
    title: str
    url: str
    published: Optional[str] = None
    source: Optional[str] = None
    snippet: Optional[str] = None
    content_available: bool
    content_hash: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ArticleChunkHistory(BaseModel):
    id: int
    article_id: int
    chunk_index: int
    content: str
    content_hash: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True