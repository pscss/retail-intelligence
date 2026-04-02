"""Task service — business logic for task registry."""

from sqlalchemy.ext.asyncio import AsyncSession

from data_service.crud.task import task_crud
from data_service.exceptions import TaskInactiveError, TaskNotFoundError
from shared.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)


class TaskService:
    """Business logic for task registry operations."""

    async def get_all_active(self, db: AsyncSession) -> TaskListResponse:
        """Get all active tasks."""
        items = await task_crud.get_all_active(db)
        return TaskListResponse(
            items=[TaskResponse.model_validate(i) for i in items],
            total=len(items),
        )

    async def get_by_name(self, db: AsyncSession, name: str) -> TaskResponse:
        """Get a task by name, raise if not found or inactive."""
        task = await task_crud.get_by_name(db, name)
        if not task:
            raise TaskNotFoundError(
                message=f"Task {name} not found",
                service="data_service",
            )
        if not task.is_active:
            raise TaskInactiveError(
                message=f"Task {name} is inactive",
                service="data_service",
            )
        return TaskResponse.model_validate(task)

    async def create(self, db: AsyncSession, data: TaskCreate) -> TaskResponse:
        """Register a new task."""
        task = await task_crud.create(db, data)
        return TaskResponse.model_validate(task)

    async def update(
        self, db: AsyncSession, name: str, data: TaskUpdate
    ) -> TaskResponse:
        """Update a task by name."""
        task = await task_crud.get_by_name(db, name)
        if not task:
            raise TaskNotFoundError(
                message=f"Task {name} not found",
                service="data_service",
            )
        updated = await task_crud.update(db, task.id, data)
        return TaskResponse.model_validate(updated)


task_service = TaskService()
