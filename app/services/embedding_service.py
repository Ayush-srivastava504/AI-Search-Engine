import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def embed_documents(self, documents: list[str]) -> np.ndarray:
        embeddings = self.model.encode(documents, convert_to_numpy=True)
        return embeddings.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding.astype(np.float32)