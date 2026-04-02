"""Standard error response schema used across all services."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error shape returned by all HTTP endpoints."""

    error: str
    detail: str | None = None
    service: str | None = None
