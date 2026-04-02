"""Query log service — business logic for query logs."""

from sqlalchemy.ext.asyncio import AsyncSession

from data_service.crud.query_log import query_log_crud
from shared.schemas.query_log import (
    QueryLogCreate,
    QueryLogListResponse,
    QueryLogResponse,
)


class QueryLogService:
    """Business logic for query log operations."""

    async def create(self, db: AsyncSession, data: QueryLogCreate) -> QueryLogResponse:
        """Create a query log entry."""
        log = await query_log_crud.create(db, data)
        return QueryLogResponse.model_validate(log)

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> QueryLogListResponse:
        """Get paginated query logs."""
        items, total = await query_log_crud.get_all(db, skip=skip, limit=limit)
        return QueryLogListResponse(
            items=[QueryLogResponse.model_validate(i) for i in items],
            total=total,
        )


query_log_service = QueryLogService()
