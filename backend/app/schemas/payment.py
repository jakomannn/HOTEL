from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PaymentBase(BaseModel):
    reservation_id: int

    amount: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    method: Optional[str] = Field(
        default=None,
        max_length=50
    )

    status: str = Field(
        default="pending",
        max_length=50
    )


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    method: Optional[str] = Field(
        default=None,
        max_length=50
    )

    status: Optional[str] = Field(
        default=None,
        max_length=50
    )


class PaymentResponse(PaymentBase):
    payment_id: int
    payment_date: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)