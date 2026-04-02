"""Inference request schemas."""

from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    """Base request schema for all inference tasks."""

    text: str = Field(..., min_length=1, max_length=512)


class TriageRequest(InferenceRequest):
    """Triage request — same as base for now, can extend later."""

    pass
