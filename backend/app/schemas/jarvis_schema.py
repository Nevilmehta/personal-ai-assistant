from pydantic import BaseModel
from typing import List, Optional, Dict, Any

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