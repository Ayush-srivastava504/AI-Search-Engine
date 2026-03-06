import faiss
import numpy as np
import os
from typing import Optional


class FAISSStore:
    def __init__(self, embedding_dim: int):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.id_map = []
        self.metadata = {}

    def add(self, embeddings: np.ndarray, doc_ids: list[str], metadata: list[dict]) -> None:
        self.index.add(embeddings)
        self.id_map.extend(doc_ids)
        for doc_id, meta in zip(doc_ids, metadata):
            self.metadata[doc_id] = meta

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> tuple[list[str], list[float]]:
        query_embedding = query_embedding.reshape(1, -1)
        distances, indices = self.index.search(query_embedding, top_k)
        
        doc_ids = [self.id_map[i] for i in indices[0]]
        scores = [float(1 / (1 + d)) for d in distances[0]]
        
        return doc_ids, scores

    def save(self, index_path: str, metadata_path: str) -> None:
        os.makedirs(os.path.dirname(index_path) if os.path.dirname(index_path) else ".", exist_ok=True)
        faiss.write_index(self.index, index_path)
        
        import json
        with open(metadata_path, "w") as f:
            json.dump({
                "id_map": self.id_map,
                "metadata": self.metadata
            }, f)

    def load(self, index_path: str, metadata_path: str) -> None:
        self.index = faiss.read_index(index_path)
        
        import json
        with open(metadata_path, "r") as f:
            data = json.load(f)
            self.id_map = data["id_map"]
            self.metadata = data["metadata"]