"""Query log ORM model."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from data_service.enums.operation_type import OperationType
from data_service.enums.served_from import ServedFrom
from data_service.session import Base


class QueryLog(Base):
    """Logs all inference and retrieval requests."""

    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operation: Mapped[OperationType] = mapped_column(
        Enum(OperationType), nullable=False, index=True
    )
    input_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    result_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    served_from: Mapped[ServedFrom | None] = mapped_column(
        Enum(ServedFrom), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )
