from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PositionBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None


class PositionResponse(PositionBase):
    position_id: int

    model_config = ConfigDict(from_attributes=True)