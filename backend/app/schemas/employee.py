from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str = Field(..., max_length=20)
    position_id: int
    status: bool = True


class EmployeeCreate(EmployeeBase):
    password: str = Field(
        ...,
        min_length=6,
        max_length=255
    )


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    position_id: Optional[int] = None
    status: Optional[bool] = None

    password: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=255
    )


class EmployeeResponse(EmployeeBase):
    employee_id: int

    model_config = ConfigDict(from_attributes=True)