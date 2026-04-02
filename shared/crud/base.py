"""Base CRUD class — inherited by all service-specific CRUD classes."""

from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.session import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchema = TypeVar("CreateSchema")
UpdateSchema = TypeVar("UpdateSchema")


class BaseCRUD(Generic[ModelType, CreateSchema, UpdateSchema]):
    """Generic CRUD operations for any SQLAlchemy model."""

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        """Get a single record by primary key."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> tuple[list[ModelType], int]:
        """Get paginated records and total count in a single query."""
        count_col = func.count().over().label("total")
        stmt = (
            select(self.model, count_col)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.id)
        )
        result = await db.execute(stmt)
        rows = result.all()
        if not rows:
            return [], 0
        items = [row[0] for row in rows]
        total = rows[0][1]
        return items, total

    async def create(self, db: AsyncSession, data: CreateSchema) -> ModelType:
        """Create a single record."""
        obj = self.model(**data.model_dump())
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def bulk_create(
        self, db: AsyncSession, data: list[CreateSchema]
    ) -> list[ModelType]:
        """Create multiple records in one transaction."""
        objs = [self.model(**item.model_dump()) for item in data]
        db.add_all(objs)
        await db.flush()
        for obj in objs:
            await db.refresh(obj)
        return objs

    async def update(
        self, db: AsyncSession, id: int, data: UpdateSchema
    ) -> ModelType | None:
        """Update a single record by primary key."""
        obj = await self.get(db, id)
        if not obj:
            return None
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(obj, key, value)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def bulk_update(
        self, db: AsyncSession, updates: list[tuple[int, UpdateSchema]]
    ) -> list[ModelType]:
        """Update multiple records. Takes list of (id, update_schema) tuples."""
        updated = []
        for id, data in updates:
            obj = await self.update(db, id, data)
            if obj:
                updated.append(obj)
        return updated

    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete a single record by primary key."""
        obj = await self.get(db, id)
        if not obj:
            return False
        await db.delete(obj)
        await db.flush()
        return True
