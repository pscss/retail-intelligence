"""FAQ Pydantic schemas."""

from pydantic import BaseModel


class FAQBase(BaseModel):
    """Shared FAQ fields."""

    question: str
    answer: str
    intent_label: str | None = None
    source: str = "bitext"


class FAQCreate(FAQBase):
    """Schema for creating a FAQ."""

    pass


class FAQResponse(FAQBase):
    """Schema for returning a FAQ."""

    id: int

    model_config = {"from_attributes": True}


class FAQListResponse(BaseModel):
    """Schema for returning a list of FAQs."""

    items: list[FAQResponse]
    total: int
