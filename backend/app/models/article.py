from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class ArticleSource(str, Enum):
    DEVTO = "devto"
    MEDIUM = "medium"
    HACKERNEWS = "hackernews"


class Article(BaseModel):
    id: str
    title: str
    content: str
    excerpt: str
    url: str
    source: ArticleSource
    author: str
    author_followers: int = 0
    published_at: datetime
    updated_at: Optional[datetime] = None
    views: int = 0
    likes: int = 0
    comments: int = 0
    tags: list[str] = []
    image_url: Optional[str] = None


class SearchResult(BaseModel):
    id: str
    title: str
    excerpt: str
    snippet: str
    url: str
    source: ArticleSource
    author: str
    published_at: datetime
    views: int
    likes: int
    relevance_score: float
    semantic_score: float
    ranking_score: float
    tags: list[str] = []


class SearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=10, ge=1, le=100)
    site: Optional[str] = None
    author: Optional[str] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    sort_by: str = Field(default="relevance", pattern="^(relevance|recent|trending)$")


class SearchResponse(BaseModel):
    query: str
    filters_applied: dict
    total_results: int
    results: list[SearchResult]
    execution_time_ms: float
    trending_topics: Optional[list[str]] = None


class TrendingTopic(BaseModel):
    topic: str
    score: float
    articles_count: int
    trend_direction: str