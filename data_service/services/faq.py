"""FAQ service — business logic for FAQs."""

from sqlalchemy.ext.asyncio import AsyncSession

from data_service.crud.faq import faq_crud
from data_service.exceptions import FAQNotFoundError
from shared.schemas.faq import FAQCreate, FAQListResponse, FAQResponse


class FAQService:
    """Business logic for FAQ operations."""

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> FAQListResponse:
        """Get paginated list of FAQs."""
        items, total = await faq_crud.get_all(db, skip=skip, limit=limit)
        return FAQListResponse(
            items=[FAQResponse.model_validate(i) for i in items],
            total=total,
        )

    async def get_by_id(self, db: AsyncSession, id: int) -> FAQResponse:
        """Get a single FAQ by ID."""
        faq = await faq_crud.get(db, id)
        if not faq:
            raise FAQNotFoundError(
                message=f"FAQ {id} not found",
                service="data_service",
            )
        return FAQResponse.model_validate(faq)

    async def create(self, db: AsyncSession, data: FAQCreate) -> FAQResponse:
        """Create a FAQ."""
        faq = await faq_crud.create(db, data)
        return FAQResponse.model_validate(faq)

    async def bulk_create(
        self, db: AsyncSession, data: list[FAQCreate]
    ) -> FAQListResponse:
        """Bulk create FAQs."""
        items = await faq_crud.bulk_create(db, data)
        return FAQListResponse(
            items=[FAQResponse.model_validate(i) for i in items],
            total=len(items),
        )


faq_service = FAQService()
