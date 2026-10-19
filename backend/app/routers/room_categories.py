from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin, require_admin_with_audit
from app.database.session import get_db
from app.schemas.room_category import (
    RoomCategoryCreate,
    RoomCategoryUpdate,
    RoomCategoryResponse,
)
from app.services.room_category_service import (
    create_room_category,
    delete_room_category,
    get_room_categories,
    get_room_category_by_id,
    update_room_category,
)


router = APIRouter(
    prefix="/room-categories",
    tags=["Room Categories"]
)


@router.post(
    "/",
    response_model=RoomCategoryResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_room_category_endpoint(
    category_data: RoomCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await create_room_category(db, category_data)


@router.get(
    "/",
    response_model=list[RoomCategoryResponse]
)
async def get_room_categories_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin)
):
    return await get_room_categories(db, skip, limit)


@router.get(
    "/{category_id}",
    response_model=RoomCategoryResponse
)
async def get_room_category_endpoint(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin)
):
    return await get_room_category_by_id(db, category_id)


@router.patch(
    "/{category_id}",
    response_model=RoomCategoryResponse
)
async def update_room_category_endpoint(
    category_id: int,
    category_data: RoomCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await update_room_category(db, category_id, category_data)


@router.delete(
    "/{category_id}",
    response_model=RoomCategoryResponse
)
async def delete_room_category_endpoint(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await delete_room_category(db, category_id)