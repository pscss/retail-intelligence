"""Query log router — HTTP endpoints for query log operations."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.services.query_log import query_log_service
from data_service.session import get_db
from shared.schemas.query_log import (
    QueryLogCreate,
    QueryLogListResponse,
    QueryLogResponse,
)

router = APIRouter(prefix="/query-logs", tags=["query-logs"])


@router.post("", response_model=QueryLogResponse)
async def create_query_log(
    data: QueryLogCreate,
    db: AsyncSession = Depends(get_db),
) -> QueryLogResponse:
    """Create a query log entry."""
    return await query_log_service.create(db, data)


@router.get("", response_model=QueryLogListResponse)
async def list_query_logs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> QueryLogListResponse:
    """List query logs with pagination."""
    return await query_log_service.get_all(db, skip=skip, limit=limit)
