import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.embedding_service import EmbeddingService
from app.services.search_service import SearchService
from app.models.search_models import Document
from app.api import search_routes

app = FastAPI(
    title="AI Semantic Search Engine",
    description="Production-grade semantic search API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_service = None
search_service = None


@app.on_event("startup")
async def startup_event():
    global embedding_service, search_service
    
    embedding_service = EmbeddingService()
    search_service = SearchService(embedding_service)
    search_routes.set_search_service(search_service)
    
    documents_path = "data/documents.json"
    if os.path.exists(documents_path):
        with open(documents_path, "r") as f:
            docs_data = json.load(f)
            documents = [Document(**doc) for doc in docs_data]
            search_service.index_documents(documents)


app.include_router(search_routes.router)


@app.get("/")
async def root():
    return {"message": "AI Semantic Search Engine is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)