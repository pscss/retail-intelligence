"""Query log CRUD operations."""

# Extends shared.crud.base.BaseCRUD
# Only add query log specific queries here

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.enums.operation_type import OperationType
from data_service.models.query_log import QueryLog
from shared.crud.base import BaseCRUD
from shared.schemas.query_log import QueryLogCreate, QueryLogResponse


class QueryLogCRUD(BaseCRUD[QueryLog, QueryLogCreate, QueryLogResponse]):
    """Query log specific database operations."""

    def __init__(self) -> None:
        super().__init__(QueryLog)

    async def get_by_operation(
        self,
        db: AsyncSession,
        operation: OperationType,
        skip: int = 0,
        limit: int = 100,
    ) -> list[QueryLog]:
        """Get all logs for a specific operation type."""
        result = await db.execute(
            select(QueryLog)
            .where(QueryLog.operation == operation)
            .order_by(QueryLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


query_log_crud = QueryLogCRUD()
