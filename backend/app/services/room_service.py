from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import Room
from app.schemas.room import RoomCreate, RoomUpdate
from app.services.room_category_service import get_room_category_by_id


async def get_room_by_id(
    db: AsyncSession,
    room_id: int
) -> Room:
    result = await db.execute(
        select(Room).where(Room.room_id == room_id)
    )

    room = result.scalar_one_or_none()

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    return room


async def get_rooms(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Room]:
    result = await db.execute(
        select(Room)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_rooms_by_status(
    db: AsyncSession,
    room_status: str,
    skip: int = 0,
    limit: int = 100
) -> list[Room]:
    result = await db.execute(
        select(Room)
        .where(Room.status == room_status)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_rooms_by_category(
    db: AsyncSession,
    category_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[Room]:
    await get_room_category_by_id(db, category_id)

    result = await db.execute(
        select(Room)
        .where(Room.category_id == category_id)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_room_by_number(
    db: AsyncSession,
    room_number: int
) -> Room | None:
    result = await db.execute(
        select(Room).where(Room.room_number == room_number)
    )

    return result.scalar_one_or_none()


async def create_room(
    db: AsyncSession,
    room_data: RoomCreate
) -> Room:
    await get_room_category_by_id(db, room_data.category_id)

    existing_room = await get_room_by_number(
        db,
        room_data.room_number
    )

    if existing_room is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room with this number already exists"
        )

    room = Room(
        **room_data.model_dump()
    )

    db.add(room)

    try:
        await db.commit()
        await db.refresh(room)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room data violates database constraints"
        )

    return room


async def update_room(
    db: AsyncSession,
    room_id: int,
    room_data: RoomUpdate
) -> Room:
    room = await get_room_by_id(db, room_id)

    update_data = room_data.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        await get_room_category_by_id(db, update_data["category_id"])

    if "room_number" in update_data:
        existing_room = await get_room_by_number(
            db,
            update_data["room_number"]
        )

        if (
            existing_room is not None
            and existing_room.room_id != room_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room with this number already exists"
            )

    for field, value in update_data.items():
        setattr(room, field, value)

    try:
        await db.commit()
        await db.refresh(room)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room data violates database constraints"
        )

    return room


async def mark_room_as_free(
    db: AsyncSession,
    room_id: int
) -> Room:
    room = await get_room_by_id(db, room_id)

    if room.status == "free":
        return room

    room.status = "free"

    try:
        await db.commit()
        await db.refresh(room)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room cannot be marked as free"
        )

    return room


async def mark_room_as_occupied(
    db: AsyncSession,
    room_id: int
) -> Room:
    room = await get_room_by_id(db, room_id)

    if room.status == "occupied":
        return room

    room.status = "occupied"

    try:
        await db.commit()
        await db.refresh(room)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room cannot be marked as occupied"
        )

    return room


async def mark_room_as_cleaning(
    db: AsyncSession,
    room_id: int
) -> Room:
    room = await get_room_by_id(db, room_id)

    if room.status == "cleaning":
        return room

    room.status = "cleaning"

    try:
        await db.commit()
        await db.refresh(room)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room cannot be marked as cleaning"
        )

    return room


async def delete_room(
    db: AsyncSession,
    room_id: int
) -> Room:
    room = await get_room_by_id(db, room_id)

    try:
        await db.delete(room)
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room cannot be deleted because it has related records"
        )

    return room