"""Product Pydantic schemas."""

from pydantic import BaseModel


class ProductBase(BaseModel):
    """Shared product fields."""

    commodity_desc: str
    sub_commodity_desc: str | None = None
    department: str | None = None


class ProductCreate(ProductBase):
    """Schema for creating a product."""

    product_id: str


class ProductResponse(ProductBase):
    """Schema for returning a product."""

    id: int
    product_id: str

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Schema for returning a list of products."""

    items: list[ProductResponse]
    total: int
