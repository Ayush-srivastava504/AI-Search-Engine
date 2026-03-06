from sentence_transformers import SentenceTransformer
import numpy as np
from app.config import settings


class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> list[float]:
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.astype(np.float32).tolist()

    def get_embedding_dim(self) -> int:
        return self.embedding_dim