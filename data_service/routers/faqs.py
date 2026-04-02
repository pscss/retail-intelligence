"""FAQ router — HTTP endpoints for FAQ operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.exceptions import FAQNotFoundError
from data_service.services.faq import faq_service
from data_service.session import get_db
from shared.schemas.error import ErrorResponse
from shared.schemas.faq import FAQCreate, FAQListResponse, FAQResponse

router = APIRouter(prefix="/faqs", tags=["faqs"])


@router.get("", response_model=FAQListResponse)
async def list_faqs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> FAQListResponse:
    """List all FAQs with pagination."""
    return await faq_service.get_all(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=FAQResponse)
async def get_faq(
    id: int,
    db: AsyncSession = Depends(get_db),
) -> FAQResponse:
    """Get a single FAQ by ID."""
    try:
        return await faq_service.get_by_id(db, id)
    except FAQNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error="faq_not_found",
                detail=e.message,
                service=e.service,
            ).model_dump(),
        ) from e


@router.post("", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(
    data: FAQCreate,
    db: AsyncSession = Depends(get_db),
) -> FAQResponse:
    """Create a single FAQ."""
    return await faq_service.create(db, data)


@router.post(
    "/bulk", response_model=FAQListResponse, status_code=status.HTTP_201_CREATED
)
async def bulk_create_faqs(
    data: list[FAQCreate],
    db: AsyncSession = Depends(get_db),
) -> FAQListResponse:
    """Bulk create FAQs."""
    return await faq_service.bulk_create(db, data)
