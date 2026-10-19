from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.payment import PaymentResponse


class ReservationBase(BaseModel):
    client_id: int
    room_id: int
    employee_id: int

    check_in_date: datetime
    check_out_date: datetime

    status: str = Field(
        default="pending",
        max_length=50
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out_date <= self.check_in_date:
            raise ValueError("check_out_date must be later than check_in_date")

        return self


class ReservationCreate(ReservationBase):
    pass


class GuestReservationCreate(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=20)
    passport_number: str = Field(..., max_length=20)

    room_id: int

    check_in_date: datetime
    check_out_date: datetime

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out_date <= self.check_in_date:
            raise ValueError("check_out_date must be later than check_in_date")

        return self


class GuestReservationsByPhoneRequest(BaseModel):
    phone: str = Field(..., max_length=20)


class GuestReservationPublicResponse(BaseModel):
    reservation_id: int

    room_number: int
    check_in_date: datetime
    check_out_date: datetime

    amount: Optional[Decimal] = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    payment_id: Optional[int] = None
    can_pay: bool

    display_status: str


class ReservationUpdate(BaseModel):
    client_id: Optional[int] = None
    room_id: Optional[int] = None
    employee_id: Optional[int] = None

    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None

    status: Optional[str] = Field(
        default=None,
        max_length=50
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


class ReservationResponse(ReservationBase):
    reservation_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReservationWithPaymentResponse(BaseModel):
    reservation: ReservationResponse
    payment: PaymentResponse

    model_config = ConfigDict(from_attributes=True)