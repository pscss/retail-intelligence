"""Retrieval request schemas."""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Semantic product search request."""

    query: str = Field(..., min_length=1, max_length=512)
    top_k: int = Field(default=5, ge=1, le=20)


class FAQRequest(BaseModel):
    """FAQ RAG request."""

    question: str = Field(..., min_length=1, max_length=512)
    top_k: int = Field(default=3, ge=1, le=10)
