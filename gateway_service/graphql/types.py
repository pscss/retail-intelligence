"""GraphQL types for gateway service."""

from enum import StrEnum

import strawberry


@strawberry.type
class HealthType:
    """Health check response."""

    service: str
    status: str


@strawberry.enum
class OperationTypeEnum(StrEnum):
    """Supported operation types."""

    SENTIMENT = "SENTIMENT"
    INTENT = "INTENT"
    TRIAGE = "TRIAGE"
    SEARCH = "SEARCH"
    FAQ = "FAQ"


@strawberry.enum
class ServedFromEnum(StrEnum):
    """Whether the response came from model or cache."""

    MODEL = "MODEL"
    CACHE = "CACHE"


@strawberry.type
class InferenceResultType:
    """Common inference result shape."""

    label: str
    score: float
    model: str
    latency_ms: int
    cached: bool


@strawberry.type
class IntentResultType(InferenceResultType):
    """Intent response with optional score map."""

    all_scores: str | None = None


@strawberry.type
class TriageResultType(InferenceResultType):
    """Triage response with category."""

    category: str | None = None


@strawberry.type
class ProductResultType:
    """Semantic search product result."""

    product_id: str
    commodity_desc: str
    department: str | None
    similarity_score: float


@strawberry.type
class SearchResultType:
    """Search response."""

    query: str
    total_results: int
    model: str
    latency_ms: int
    cached: bool
    results: list[ProductResultType]


@strawberry.type
class FAQResultType:
    """Single FAQ retrieval result."""

    question: str
    answer: str
    intent_label: str | None
    similarity_score: float


@strawberry.type
class RagResultType:
    """RAG response."""

    question: str
    total_results: int
    model: str
    latency_ms: int
    cached: bool
    results: list[FAQResultType]
