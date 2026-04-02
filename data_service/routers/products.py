"""Product router — HTTP endpoints for product operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.exceptions import DuplicateProductError, ProductNotFoundError
from data_service.services.product import product_service
from data_service.session import get_db
from shared.schemas.error import ErrorResponse
from shared.schemas.product import ProductCreate, ProductListResponse, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    """List all products with pagination."""
    return await product_service.get_all(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=ProductResponse)
async def get_product(
    id: int,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Get a single product by ID."""
    try:
        return await product_service.get_by_id(db, id)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error="product_not_found",
                detail=e.message,
                service=e.service,
            ).model_dump(),
        ) from e


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Create a single product."""
    try:
        return await product_service.create(db, data)
    except DuplicateProductError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ErrorResponse(
                error="duplicate_product",
                detail=e.message,
                service=e.service,
            ).model_dump(),
        ) from e


@router.post(
    "/bulk", response_model=ProductListResponse, status_code=status.HTTP_201_CREATED
)
async def bulk_create_products(
    data: list[ProductCreate],
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    """Bulk create products."""
    return await product_service.bulk_create(db, data)
