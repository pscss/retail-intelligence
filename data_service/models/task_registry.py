"""Task registry ORM model."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from data_service.enums.task_operation_type import TaskOperationType
from data_service.session import Base


class TaskRegistry(Base):
    """Registry of all available tasks and their service locations."""

    __tablename__ = "task_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str | None] = mapped_column(String(200), nullable=True)
    service_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    operation_type: Mapped[TaskOperationType | None] = mapped_column(
        Enum(TaskOperationType), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
