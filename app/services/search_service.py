import numpy as np
from app.services.embedding_service import EmbeddingService
from app.vectorstore.faiss_store import FAISSStore
from app.models.search_models import Document, SearchResult


class SearchService:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.vector_store = FAISSStore(embedding_service.embedding_dim)
        self.documents = {}

    def index_documents(self, documents: list[Document]) -> None:
        doc_ids = [doc.id for doc in documents]
        contents = [doc.content for doc in documents]
        metadata = [{"title": doc.title, **doc.metadata or {}} for doc in documents]
        
        embeddings = self.embedding_service.embed_documents(contents)
        self.vector_store.add(embeddings, doc_ids, metadata)
        
        for doc in documents:
            self.documents[doc.id] = doc

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        query_embedding = self.embedding_service.embed_query(query)
        doc_ids, scores = self.vector_store.search(query_embedding, top_k)
        
        results = []
        for doc_id, score in zip(doc_ids, scores):
            doc = self.documents[doc_id]
            results.append(SearchResult(
                id=doc.id,
                title=doc.title,
                content=doc.content,
                score=score,
                metadata=doc.metadata
            ))
        
        return results

    def save_index(self, index_path: str, metadata_path: str) -> None:
        self.vector_store.save(index_path, metadata_path)

    def load_index(self, index_path: str, metadata_path: str, documents: list[Document]) -> None:
        self.vector_store.load(index_path, metadata_path)
        for doc in documents:
            self.documents[doc.id] = doc