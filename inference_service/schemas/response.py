"""Inference response schemas."""

from pydantic import BaseModel


class InferenceResponse(BaseModel):
    """Base response schema for all inference tasks."""

    label: str
    score: float
    model: str
    latency_ms: int
    cached: bool = False


class SentimentResponse(InferenceResponse):
    """Sentiment analysis response."""

    pass


class IntentResponse(InferenceResponse):
    """Intent classification response."""

    all_scores: dict[str, float] | None = None


class TriageResponse(InferenceResponse):
    """Complaint triage response."""

    category: str | None = None
