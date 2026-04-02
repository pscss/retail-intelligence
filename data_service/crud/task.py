"""Task registry CRUD operations."""

# Extends shared.crud.base.BaseCRUD
# Only add task-specific queries here

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.models.task_registry import TaskRegistry
from shared.crud.base import BaseCRUD
from shared.schemas.task import TaskCreate, TaskUpdate


class TaskCRUD(BaseCRUD[TaskRegistry, TaskCreate, TaskUpdate]):
    """Task registry specific database operations."""

    def __init__(self) -> None:
        super().__init__(TaskRegistry)

    async def get_by_name(self, db: AsyncSession, name: str) -> TaskRegistry | None:
        """Get a task by its unique name."""
        result = await db.execute(select(TaskRegistry).where(TaskRegistry.name == name))
        return result.scalar_one_or_none()

    async def get_all_active(self, db: AsyncSession) -> list[TaskRegistry]:
        """Get all active tasks."""
        result = await db.execute(
            select(TaskRegistry).where(TaskRegistry.is_active == True)  # noqa: E712
        )
        return list(result.scalars().all())


task_crud = TaskCRUD()
