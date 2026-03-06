from pydantic import BaseModel, Field
from typing import Optional


class Document(BaseModel):
    id: str
    title: str
    content: str
    metadata: Optional[dict] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=100)


class SearchResult(BaseModel):
    id: str
    title: str
    content: str
    score: float
    metadata: Optional[dict] = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total_results: int