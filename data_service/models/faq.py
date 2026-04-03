"""FAQ ORM model."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from data_service.session import Base


class FAQ(Base):
    """Customer FAQ corpus from Bitext dataset."""

    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    intent_label: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    source: Mapped[str] = mapped_column(String(50), default="bitext")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
