"""FAQ CRUD operations."""

# Extends shared.crud.base.BaseCRUD
# Only add FAQ-specific queries here

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.models.faq import FAQ
from shared.crud.base import BaseCRUD
from shared.schemas.faq import FAQCreate, FAQResponse


class FAQCrud(BaseCRUD[FAQ, FAQCreate, FAQResponse]):
    """FAQ-specific database operations."""

    def __init__(self) -> None:
        super().__init__(FAQ)

    async def get_by_intent(
        self, db: AsyncSession, intent_label: str, skip: int = 0, limit: int = 100
    ) -> list[FAQ]:
        """Get all FAQs for a given intent label."""
        result = await db.execute(
            select(FAQ)
            .where(FAQ.intent_label == intent_label)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


faq_crud = FAQCrud()
