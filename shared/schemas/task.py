"""Task registry Pydantic schemas."""

from pydantic import BaseModel

from data_service.enums.task_operation_type import TaskOperationType


class TaskBase(BaseModel):
    """Shared task fields."""

    name: str
    description: str | None = None
    model: str | None = None
    service_url: str | None = None
    operation_type: TaskOperationType | None = None
    is_active: bool = True


class TaskCreate(TaskBase):
    """Schema for creating a task."""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    description: str | None = None
    model: str | None = None
    service_url: str | None = None
    is_active: bool | None = None


class TaskResponse(TaskBase):
    """Schema for returning a task."""

    id: int

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Schema for returning a list of tasks."""

    items: list[TaskResponse]
    total: int
