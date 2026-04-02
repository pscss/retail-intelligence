"""Retrieval response schemas."""

from pydantic import BaseModel


class ProductResult(BaseModel):
    """Single product search result."""

    product_id: str
    commodity_desc: str
    department: str | None
    similarity_score: float


class SearchResponse(BaseModel):
    """Semantic product search response."""

    query: str
    results: list[ProductResult]
    total_results: int
    model: str
    latency_ms: int
    cached: bool = False


class FAQResult(BaseModel):
    """Single FAQ retrieval result."""

    question: str
    answer: str
    intent_label: str | None
    similarity_score: float


class FAQResponse(BaseModel):
    """FAQ RAG response."""

    question: str
    results: list[FAQResult]
    total_results: int
    model: str
    latency_ms: int
    cached: bool = False
