"""Query log Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel

from data_service.enums.operation_type import OperationType
from data_service.enums.served_from import ServedFrom


class QueryLogCreate(BaseModel):
    """Schema for creating a query log entry."""

    operation: OperationType
    input_hash: str | None = None
    result_label: str | None = None
    confidence: float | None = None
    latency_ms: int | None = None
    served_from: ServedFrom | None = None


class QueryLogResponse(QueryLogCreate):
    """Schema for returning a query log entry."""

    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class QueryLogListResponse(BaseModel):
    """Schema for returning a list of query logs."""

    items: list[QueryLogResponse]
    total: int
