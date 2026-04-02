"""Pydantic schemas for gateway GraphQL inputs."""

from pydantic import BaseModel, Field


class TextInput(BaseModel):
    """Text payload for inference operations."""

    text: str = Field(..., min_length=1, max_length=512)


class SearchInput(BaseModel):
    """Payload for semantic search."""

    query: str = Field(..., min_length=1, max_length=512)
    top_k: int = Field(default=5, ge=1, le=20)


class RagInput(BaseModel):
    """Payload for FAQ retrieval."""

    question: str = Field(..., min_length=1, max_length=512)
    top_k: int = Field(default=3, ge=1, le=10)
