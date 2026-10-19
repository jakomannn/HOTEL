from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StayHistoryBase(BaseModel):
    reservation_id: Optional[int] = None
    check_in_id: Optional[int] = None

    client_id: int
    room_id: int

    check_in_date: datetime
    check_out_date: datetime

    total_nights: int = Field(
        ...,
        ge=1
    )

    total_cost: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out_date <= self.check_in_date:
            raise ValueError("check_out_date must be later than check_in_date")

        return self


class StayHistoryCreate(StayHistoryBase):
    pass


class StayHistoryUpdate(BaseModel):
    reservation_id: Optional[int] = None
    check_in_id: Optional[int] = None

    client_id: Optional[int] = None
    room_id: Optional[int] = None

    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None

    total_nights: Optional[int] = Field(
        default=None,
        ge=1
    )

    total_cost: Optional[Decimal] = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.check_in_date is not None
            and self.check_out_date is not None
            and self.check_out_date <= self.check_in_date
        ):
            raise ValueError("check_out_date must be later than check_in_date")

        return self


class StayHistoryResponse(StayHistoryBase):
    history_id: int

    model_config = ConfigDict(from_attributes=True)