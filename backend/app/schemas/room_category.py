from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RoomCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    max_guests: int = Field(..., ge=1)

    price_per_night: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=2
    )


class RoomCategoryCreate(RoomCategoryBase):
    pass


class RoomCategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    max_guests: Optional[int] = Field(default=None, ge=1)

    price_per_night: Optional[Decimal] = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2
    )


class RoomCategoryResponse(RoomCategoryBase):
    category_id: int

    model_config = ConfigDict(from_attributes=True)