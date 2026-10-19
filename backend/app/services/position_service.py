from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.position import Position
from app.schemas.position import PositionCreate, PositionUpdate


async def get_position_by_id(
    db: AsyncSession,
    position_id: int
) -> Position:
    result = await db.execute(
        select(Position).where(Position.position_id == position_id)
    )

    position = result.scalar_one_or_none()

    if position is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )

    return position


async def get_positions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Position]:
    result = await db.execute(
        select(Position)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_position_by_name(
    db: AsyncSession,
    name: str
) -> Position | None:
    result = await db.execute(
        select(Position).where(Position.name == name)
    )

    return result.scalar_one_or_none()


async def create_position(
    db: AsyncSession,
    position_data: PositionCreate
) -> Position:
    existing_position = await get_position_by_name(
        db,
        position_data.name
    )

    if existing_position is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position with this name already exists"
        )

    position = Position(
        **position_data.model_dump()
    )

    db.add(position)

    try:
        await db.commit()
        await db.refresh(position)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position data violates database constraints"
        )

    return position


async def update_position(
    db: AsyncSession,
    position_id: int,
    position_data: PositionUpdate
) -> Position:
    position = await get_position_by_id(db, position_id)

    update_data = position_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_position = await get_position_by_name(
            db,
            update_data["name"]
        )

        if (
            existing_position is not None
            and existing_position.position_id != position_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Position with this name already exists"
            )

    for field, value in update_data.items():
        setattr(position, field, value)

    try:
        await db.commit()
        await db.refresh(position)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position data violates database constraints"
        )

    return position


async def delete_position(
    db: AsyncSession,
    position_id: int
) -> Position:
    position = await get_position_by_id(db, position_id)

    try:
        await db.delete(position)
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position cannot be deleted because it has related employees"
        )

    return position