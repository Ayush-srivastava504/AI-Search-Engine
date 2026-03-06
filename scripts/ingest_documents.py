import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.embedding_service import EmbeddingService
from app.services.search_service import SearchService
from app.models.search_models import Document


def load_documents_from_json(file_path: str) -> list[Document]:
    with open(file_path, "r") as f:
        docs_data = json.load(f)
    
    return [Document(**doc) for doc in docs_data]


def ingest_documents(documents_path: str = "data/documents.json", index_dir: str = "index") -> None:
    print(f"Loading documents from {documents_path}...")
    documents = load_documents_from_json(documents_path)
    print(f"Loaded {len(documents)} documents")
    
    print("Initializing embedding service...")
    embedding_service = EmbeddingService()
    
    print("Initializing search service...")
    search_service = SearchService(embedding_service)
    
    print("Indexing documents...")
    search_service.index_documents(documents)
    print(f"Indexed {len(documents)} documents")
    
    print(f"Saving index to {index_dir}...")
    search_service.save_index(
        f"{index_dir}/faiss.index",
        f"{index_dir}/metadata.json"
    )
    print("Indexing complete!")


if __name__ == "__main__":
    ingest_documents()