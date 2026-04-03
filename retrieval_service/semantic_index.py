"""FAISS index builder and searcher for product and FAQ corpus."""

import time

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from retrieval_service.exceptions import CorpusEmptyError, IndexNotBuiltError

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


class FAISSIndex:
    """Manages a FAISS index for semantic search."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._model: SentenceTransformer | None = None
        self._index: faiss.IndexFlatIP | None = None
        self._documents: list[dict] = []
        self._built = False

    def load_model(self) -> None:
        """Load sentence transformer model."""
        print(f"Loading embedding model for {self.name}...")
        start = time.time()
        self._model = SentenceTransformer(MODEL_NAME)
        print(f"Embedding model loaded in {time.time() - start:.2f}s")

    def build(self, documents: list[dict], text_field: str) -> None:
        """Build FAISS index from documents."""
        if not documents:
            raise CorpusEmptyError(
                message=f"No documents to index for {self.name}",
                service="retrieval_service",
            )
        if not self._model:
            self.load_model()

        print(f"Building {self.name} index from {len(documents)} documents...")
        start = time.time()

        texts = [doc[text_field] for doc in documents]
        assert self._model is not None  # for type checker
        embeddings = self._model.encode(
            texts,
            batch_size=64,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

        embeddings = np.array(embeddings, dtype=np.float32)
        self._index = faiss.IndexFlatIP(EMBEDDING_DIM)
        self._index.add(embeddings)
        self._documents = documents
        self._built = True

        print(f"{self.name} index built in {time.time() - start:.2f}s")

    def search(self, query: str, top_k: int = 5) -> list[tuple[dict, float]]:
        """Search index, return list of (document, score) tuples."""
        if not self._built or not self._index:
            raise IndexNotBuiltError(
                message=f"{self.name} index not built yet",
                service="retrieval_service",
            )
        if not self._model:
            raise IndexNotBuiltError(
                message=f"Embedding model not loaded for {self.name}",
                service="retrieval_service",
            )

        query_embedding = self._model.encode(
            [query],
            normalize_embeddings=True,
        )
        query_embedding = np.array(query_embedding, dtype=np.float32)

        scores, indices = self._index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0], strict=True):
            if idx != -1:
                results.append((self._documents[idx], float(score)))

        return results

    @property
    def is_built(self) -> bool:
        """Check if index is built."""
        return self._built

    @property
    def size(self) -> int:
        """Number of documents in index."""
        return len(self._documents)


product_index = FAISSIndex(name="products")
faq_index = FAISSIndex(name="faqs")
