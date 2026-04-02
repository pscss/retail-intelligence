"""Task registry router — HTTP endpoints for task registry operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.exceptions import TaskInactiveError, TaskNotFoundError
from data_service.services.task import task_service
from data_service.session import get_db
from shared.schemas.error import ErrorResponse
from shared.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_active_tasks(
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    """List all active tasks."""
    return await task_service.get_all_active(db)


@router.get("/{name}", response_model=TaskResponse)
async def get_task(
    name: str,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Get a task by name."""
    try:
        return await task_service.get_by_name(db, name)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error="task_not_found",
                detail=e.message,
                service=e.service,
            ).model_dump(),
        ) from e
    except TaskInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(
                error="task_inactive",
                detail=e.message,
                service=e.service,
            ).model_dump(),
        ) from e


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Register a new task."""
    return await task_service.create(db, data)


@router.patch("/{name}", response_model=TaskResponse)
async def update_task(
    name: str,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Update a task by name."""
    try:
        return await task_service.update(db, name, data)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error="task_not_found",
                detail=e.message,
                service=e.service,
            ).model_dump(),
        ) from e
