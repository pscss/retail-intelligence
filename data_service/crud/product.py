"""Product CRUD operations."""

# Extends shared.crud.base.BaseCRUD
# Only add product-specific queries here
# Generic ops (get, create, update, delete, bulk) are inherited

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.models.product import Product
from shared.crud.base import BaseCRUD
from shared.schemas.product import ProductCreate, ProductResponse


class ProductCRUD(BaseCRUD[Product, ProductCreate, ProductResponse]):
    """Product-specific database operations."""

    def __init__(self) -> None:
        super().__init__(Product)

    async def get_by_product_id(
        self, db: AsyncSession, product_id: str
    ) -> Product | None:
        """Get a product by its string product_id."""
        result = await db.execute(
            select(Product).where(Product.product_id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_by_department(
        self, db: AsyncSession, department: str, skip: int = 0, limit: int = 100
    ) -> list[Product]:
        """Get all products in a department."""
        result = await db.execute(
            select(Product)
            .where(Product.department == department)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


product_crud = ProductCRUD()
