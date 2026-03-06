from fastapi import APIRouter, HTTPException, Query
from app.models.article import SearchQuery, SearchResponse, TrendingTopic
from app.search.search_service import SearchService

router = APIRouter(prefix="/api", tags=["search"])
search_service: SearchService = None


def set_search_service(service: SearchService):
    global search_service
    search_service = service


@router.post("/search", response_model=SearchResponse)
async def search(
    query: str = Query(..., min_length=1, max_length=500),
    top_k: int = Query(10, ge=1, le=100),
    sort_by: str = Query("relevance", regex="^(relevance|recent|trending)$")
):
    if not search_service:
        raise HTTPException(status_code=500, detail="Search service not initialized")

    try:
        result = search_service.hybrid_search(query, top_k=top_k, sort_by=sort_by)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return SearchResponse(
            query=result["query"],
            filters_applied=result["filters_applied"],
            total_results=result["total_results"],
            results=result["results"],
            execution_time_ms=result["execution_time_ms"],
            trending_topics=search_service.get_trending_topics()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending():
    if not search_service:
        raise HTTPException(status_code=500, detail="Search service not initialized")

    try:
        trending = search_service.get_trending_topics(days=7)
        return {
            "trending_topics": trending,
            "time_range_days": 7
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl")
async def trigger_crawl(limit_per_source: int = Query(20, ge=5, le=100)):
    if not search_service:
        raise HTTPException(status_code=500, detail="Search service not initialized")

    try:
        count = search_service.crawl_and_index_fresh(limit_per_source=limit_per_source)
        return {
            "status": "success",
            "articles_indexed": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "tech-articles-search-engine"
    }