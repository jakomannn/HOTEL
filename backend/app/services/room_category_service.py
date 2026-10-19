from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room_category import RoomCategory
from app.schemas.room_category import RoomCategoryCreate, RoomCategoryUpdate


async def get_room_category_by_id(
    db: AsyncSession,
    category_id: int
) -> RoomCategory:
    result = await db.execute(
        select(RoomCategory).where(RoomCategory.category_id == category_id)
    )

    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room category not found"
        )

    return category


async def get_room_categories(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[RoomCategory]:
    result = await db.execute(
        select(RoomCategory)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_room_category_by_name(
    db: AsyncSession,
    name: str
) -> RoomCategory | None:
    result = await db.execute(
        select(RoomCategory).where(RoomCategory.name == name)
    )

    return result.scalar_one_or_none()


async def create_room_category(
    db: AsyncSession,
    category_data: RoomCategoryCreate
) -> RoomCategory:
    existing_category = await get_room_category_by_name(
        db,
        category_data.name
    )

    if existing_category is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room category with this name already exists"
        )

    category = RoomCategory(
        **category_data.model_dump()
    )

    db.add(category)

    try:
        await db.commit()
        await db.refresh(category)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room category data violates database constraints"
        )

    return category


async def update_room_category(
    db: AsyncSession,
    category_id: int,
    category_data: RoomCategoryUpdate
) -> RoomCategory:
    category = await get_room_category_by_id(db, category_id)

    update_data = category_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_category = await get_room_category_by_name(
            db,
            update_data["name"]
        )

        if (
            existing_category is not None
            and existing_category.category_id != category_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room category with this name already exists"
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    try:
        await db.commit()
        await db.refresh(category)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room category data violates database constraints"
        )

    return category


async def delete_room_category(
    db: AsyncSession,
    category_id: int
) -> RoomCategory:
    category = await get_room_category_by_id(db, category_id)

    try:
        await db.delete(category)
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room category cannot be deleted because it has related rooms"
        )

    return category