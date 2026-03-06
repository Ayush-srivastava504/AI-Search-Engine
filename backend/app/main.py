from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from app.search.search_service import SearchService
from app.api import search_routes
import logging

logger = logging.getLogger(__name__)
search_service_instance: SearchService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global search_service_instance
    
    logger.info("Initializing search service...")
    search_service_instance = SearchService()
    search_routes.set_search_service(search_service_instance)
    
    logger.info("Search service initialized and ready")
    
    yield
    
    logger.info("Shutting down search service")


app = FastAPI(
    title="Tech Articles Search Engine",
    description="AI-powered semantic search for tech blogs, Dev.to, Medium, and Hacker News",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(search_routes.router)


@app.get("/")
async def root():
    return {
        "name": "Tech Articles Search Engine",
        "description": "AI-powered semantic search across tech blogs",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search?query=your_query&top_k=10&sort_by=relevance",
            "trending": "/api/trending",
            "crawl": "/api/crawl",
            "health": "/api/health",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)