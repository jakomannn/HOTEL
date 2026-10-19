from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


RoomStatus = Literal[
    "free",
    "occupied",
    "cleaning"
]


class RoomBase(BaseModel):
    room_number: int = Field(..., ge=1)
    category_id: int
    status: RoomStatus = "free"


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_number: Optional[int] = Field(default=None, ge=1)
    category_id: Optional[int] = None
    status: Optional[RoomStatus] = None


class RoomResponse(RoomBase):
    room_id: int

    model_config = ConfigDict(from_attributes=True)