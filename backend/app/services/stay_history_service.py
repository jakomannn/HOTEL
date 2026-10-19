from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stay_history import StayHistory
from app.schemas.stay_history import StayHistoryCreate, StayHistoryUpdate
from app.services.client_service import get_client_by_id
from app.services.room_service import get_room_by_id


async def get_stay_history_by_id(
    db: AsyncSession,
    history_id: int
) -> StayHistory:
    result = await db.execute(
        select(StayHistory).where(
            StayHistory.history_id == history_id
        )
    )

    stay_history = result.scalar_one_or_none()

    if stay_history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stay history record not found"
        )

    return stay_history


async def get_stay_history_records(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[StayHistory]:
    result = await db.execute(
        select(StayHistory)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_stay_history_by_client(
    db: AsyncSession,
    client_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[StayHistory]:
    await get_client_by_id(db, client_id)

    result = await db.execute(
        select(StayHistory)
        .where(StayHistory.client_id == client_id)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_stay_history_by_room(
    db: AsyncSession,
    room_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[StayHistory]:
    await get_room_by_id(db, room_id)

    result = await db.execute(
        select(StayHistory)
        .where(StayHistory.room_id == room_id)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_stay_history_by_reservation(
    db: AsyncSession,
    reservation_id: int
) -> StayHistory:
    result = await db.execute(
        select(StayHistory).where(
            StayHistory.reservation_id == reservation_id
        )
    )

    stay_history = result.scalar_one_or_none()

    if stay_history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stay history record not found"
        )

    return stay_history


async def get_stay_history_by_check_in(
    db: AsyncSession,
    check_in_id: int
) -> StayHistory:
    result = await db.execute(
        select(StayHistory).where(
            StayHistory.check_in_id == check_in_id
        )
    )

    stay_history = result.scalar_one_or_none()

    if stay_history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stay history record not found"
        )

    return stay_history


async def create_stay_history(
    db: AsyncSession,
    stay_history_data: StayHistoryCreate
) -> StayHistory:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Manual stay history creation is disabled. Stay history is created automatically by database trigger after check-out."
    )


async def update_stay_history(
    db: AsyncSession,
    history_id: int,
    stay_history_data: StayHistoryUpdate
) -> StayHistory:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Manual stay history update is disabled. Stay history is managed automatically by database trigger."
    )


async def delete_stay_history(
    db: AsyncSession,
    history_id: int
) -> StayHistory:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Manual stay history deletion is disabled."
    )