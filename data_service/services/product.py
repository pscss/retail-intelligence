"""Product service — business logic for products."""

from sqlalchemy.ext.asyncio import AsyncSession

from data_service.crud.product import product_crud
from data_service.exceptions import DuplicateProductError, ProductNotFoundError
from shared.schemas.product import ProductCreate, ProductListResponse, ProductResponse


class ProductService:
    """Business logic for product operations."""

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> ProductListResponse:
        """Get paginated list of products."""
        items, total = await product_crud.get_all(db, skip=skip, limit=limit)
        return ProductListResponse(
            items=[ProductResponse.model_validate(i) for i in items],
            total=total,
        )

    async def get_by_id(self, db: AsyncSession, id: int) -> ProductResponse:
        """Get a single product by ID."""
        product = await product_crud.get(db, id)
        if not product:
            raise ProductNotFoundError(
                message=f"Product {id} not found",
                service="data_service",
            )
        return ProductResponse.model_validate(product)

    async def create(self, db: AsyncSession, data: ProductCreate) -> ProductResponse:
        """Create a product, raise if duplicate."""
        existing = await product_crud.get_by_product_id(db, data.product_id)
        if existing:
            raise DuplicateProductError(
                message=f"Product {data.product_id} already exists",
                service="data_service",
            )
        product = await product_crud.create(db, data)
        return ProductResponse.model_validate(product)

    async def bulk_create(
        self, db: AsyncSession, data: list[ProductCreate]
    ) -> ProductListResponse:
        """Bulk create products."""
        items = await product_crud.bulk_create(db, data)
        return ProductListResponse(
            items=[ProductResponse.model_validate(i) for i in items],
            total=len(items),
        )


product_service = ProductService()
