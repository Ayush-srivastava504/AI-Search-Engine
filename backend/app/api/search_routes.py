from fastapi import APIRouter, HTTPException, Query
from app.models.article import SearchResponse, ArticleSource
from app.search.search_service import SearchService
import traceback

router = APIRouter(prefix="/api", tags=["search"])

search_service: SearchService | None = None


def set_search_service(service: SearchService):
    global search_service
    search_service = service


@router.get("/search", response_model=SearchResponse)
async def search(
    query: str = Query(..., min_length=1, max_length=500),
    top_k: int = Query(10, ge=1, le=100),
    sort_by: str = Query("relevance", pattern="^(relevance|recent|trending)$"),
):
    if search_service is None:
        raise HTTPException(status_code=500, detail="Search service not initialized")

    try:
        result = search_service.hybrid_search(
            query=query,
            top_k=top_k,
            sort_by=sort_by,
        )

        if not result:
            raise HTTPException(status_code=404, detail="No results found")

        results = result.get("results", [])

        cleaned_results = []
        for r in results:
            r_dict = r.model_dump() if hasattr(r, 'model_dump') else (r.dict() if hasattr(r, 'dict') else r)
            
            cleaned_results.append(
                {
                    "id": r_dict.get("id"),
                    "title": r_dict.get("title"),
                    "excerpt": r_dict.get("excerpt", ""),
                    "snippet": r_dict.get("snippet", r_dict.get("excerpt", "")),
                    "url": r_dict.get("url"),
                    "source": r_dict.get("source", "hackernews"),
                    "author": r_dict.get("author", "Unknown"),
                    "published_at": r_dict.get("published_at"),
                    "views": r_dict.get("views", 0),
                    "likes": r_dict.get("likes", 0),
                    "relevance_score": r_dict.get("relevance_score", r_dict.get("ranking_score", 0.0)),
                    "semantic_score": r_dict.get("semantic_score", 0.0),
                    "ranking_score": r_dict.get("ranking_score", 0.0),
                    "tags": r_dict.get("tags", []),
                }
            )

        return SearchResponse(
            query=result.get("query", query),
            filters_applied=result.get("filters_applied", {}),
            total_results=result.get("total_results", len(cleaned_results)),
            results=cleaned_results,
            execution_time_ms=result.get("execution_time_ms", 0),
            trending_topics=search_service.get_trending_topics(),
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))


@router.get("/trending")
async def get_trending():
    if search_service is None:
        raise HTTPException(status_code=500, detail="Search service not initialized")

    try:
        trending = search_service.get_trending_topics(days=7)

        return {
            "trending_topics": trending,
            "time_range_days": 7,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))


@router.post("/crawl")
async def trigger_crawl(limit_per_source: int = Query(20, ge=5, le=100)):
    if search_service is None:
        raise HTTPException(status_code=500, detail="Search service not initialized")

    try:
        count = search_service.crawl_and_index_fresh(limit_per_source=limit_per_source)

        return {
            "status": "success",
            "articles_indexed": count,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "tech-articles-search-engine",
    }