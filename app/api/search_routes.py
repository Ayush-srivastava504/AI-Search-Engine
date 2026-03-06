from fastapi import APIRouter, HTTPException
from app.models.search_models import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/api", tags=["search"])
search_service: SearchService = None


def set_search_service(service: SearchService) -> None:
    global search_service
    search_service = service


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    if search_service is None:
        raise HTTPException(status_code=500, detail="Search service not initialized")
    
    if not search_service.documents:
        raise HTTPException(status_code=400, detail="No documents indexed")
    
    results = search_service.search(request.query, request.top_k)
    
    return SearchResponse(
        query=request.query,
        results=results,
        total_results=len(results)
    )


@router.get("/health")
async def health_check() -> dict:
    return {"status": "healthy"}