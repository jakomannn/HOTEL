from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class CheckInCreate(BaseModel):
    reservation_id: int
    employee_id: int
    check_in_time: Optional[datetime] = None


class CheckInUpdate(BaseModel):
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_times(self):
        if (
            self.check_in_time is not None
            and self.check_out_time is not None
            and self.check_out_time <= self.check_in_time
        ):
            raise ValueError("check_out_time must be later than check_in_time")

        return self


class CheckOutRequest(BaseModel):
    check_out_time: Optional[datetime] = None


class CheckInResponse(BaseModel):
    check_in_id: int
    reservation_id: int
    employee_id: int

    check_in_time: datetime
    check_out_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)