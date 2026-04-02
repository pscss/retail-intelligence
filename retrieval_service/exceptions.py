"""Retrieval service exceptions."""

from shared.exceptions import RetailIntelligenceError


class IndexNotBuiltError(RetailIntelligenceError):
    """Raised when FAISS index has not been built yet."""


class EmbeddingError(RetailIntelligenceError):
    """Raised when embedding generation fails."""


class CorpusEmptyError(RetailIntelligenceError):
    """Raised when corpus has no documents to index."""


class SearchError(RetailIntelligenceError):
    """Raised when search fails."""
