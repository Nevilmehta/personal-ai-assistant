from pydantic import BaseModel
from typing import List, Optional

class JarvisAskRequest(BaseModel):
    query: str
    mode: Optional[str] = "auto"

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