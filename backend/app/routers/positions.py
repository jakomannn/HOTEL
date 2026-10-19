from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin, require_admin_with_audit
from app.database.session import get_db
from app.schemas.position import PositionCreate, PositionUpdate, PositionResponse
from app.services.position_service import (
    create_position,
    delete_position,
    get_position_by_id,
    get_positions,
    update_position,
)


router = APIRouter(
    prefix="/positions",
    tags=["Positions"]
)


@router.post(
    "/",
    response_model=PositionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_position_endpoint(
    position_data: PositionCreate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await create_position(db, position_data)


@router.get(
    "/",
    response_model=list[PositionResponse]
)
async def get_positions_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin)
):
    return await get_positions(db, skip, limit)


@router.get(
    "/{position_id}",
    response_model=PositionResponse
)
async def get_position_endpoint(
    position_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin)
):
    return await get_position_by_id(db, position_id)


@router.patch(
    "/{position_id}",
    response_model=PositionResponse
)
async def update_position_endpoint(
    position_id: int,
    position_data: PositionUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await update_position(db, position_id, position_data)


@router.delete(
    "/{position_id}",
    response_model=PositionResponse
)
async def delete_position_endpoint(
    position_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await delete_position(db, position_id)