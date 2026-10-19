from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    require_admin,
    require_admin_with_audit,
    require_manager,
    require_manager_with_audit,
)
from app.database.session import get_db
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse
from app.services.room_service import (
    create_room,
    delete_room,
    get_room_by_id,
    get_rooms,
    get_rooms_by_category,
    get_rooms_by_status,
    mark_room_as_free,
    update_room,
)


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)


@router.post(
    "/",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_room_endpoint(
    room_data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await create_room(db, room_data)


@router.get(
    "/",
    response_model=list[RoomResponse]
)
async def get_rooms_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager)
):
    return await get_rooms(db, skip, limit)


@router.get(
    "/status/{room_status}",
    response_model=list[RoomResponse]
)
async def get_rooms_by_status_endpoint(
    room_status: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager)
):
    return await get_rooms_by_status(db, room_status, skip, limit)


@router.get(
    "/category/{category_id}",
    response_model=list[RoomResponse]
)
async def get_rooms_by_category_endpoint(
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager)
):
    return await get_rooms_by_category(db, category_id, skip, limit)


@router.patch(
    "/{room_id}/mark-free",
    response_model=RoomResponse
)
async def mark_room_as_free_endpoint(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await mark_room_as_free(db, room_id)


@router.get(
    "/{room_id}",
    response_model=RoomResponse
)
async def get_room_endpoint(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager)
):
    return await get_room_by_id(db, room_id)


@router.patch(
    "/{room_id}",
    response_model=RoomResponse
)
async def update_room_endpoint(
    room_id: int,
    room_data: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await update_room(db, room_id, room_data)


@router.delete(
    "/{room_id}",
    response_model=RoomResponse
)
async def delete_room_endpoint(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await delete_room(db, room_id)