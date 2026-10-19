from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.check_in import CheckIn
from app.schemas.check_in import CheckInCreate, CheckInUpdate
from app.services.employee_service import get_employee_by_id
from app.services.reservation_service import get_reservation_by_id
from app.services.room_service import get_room_by_id


async def get_check_in_by_id(
    db: AsyncSession,
    check_in_id: int
) -> CheckIn:
    result = await db.execute(
        select(CheckIn).where(CheckIn.check_in_id == check_in_id)
    )

    check_in = result.scalar_one_or_none()

    if check_in is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in record not found"
        )

    return check_in


async def get_check_ins(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[CheckIn]:
    result = await db.execute(
        select(CheckIn)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_check_ins_by_reservation(
    db: AsyncSession,
    reservation_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[CheckIn]:
    await get_reservation_by_id(db, reservation_id)

    result = await db.execute(
        select(CheckIn)
        .where(CheckIn.reservation_id == reservation_id)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_check_ins_by_employee(
    db: AsyncSession,
    employee_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[CheckIn]:
    await get_employee_by_id(db, employee_id)

    result = await db.execute(
        select(CheckIn)
        .where(CheckIn.employee_id == employee_id)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def create_check_in(
    db: AsyncSession,
    check_in_data: CheckInCreate
) -> CheckIn:
    reservation = await get_reservation_by_id(
        db,
        check_in_data.reservation_id
    )

    await get_employee_by_id(
        db,
        check_in_data.employee_id
    )

    room = await get_room_by_id(db, reservation.room_id)

    if reservation.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create check-in for cancelled reservation"
        )

    if reservation.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create check-in for completed reservation"
        )

    if reservation.status != "confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create check-in for unpaid or unconfirmed reservation"
        )

    if room.status == "occupied":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is already occupied"
        )

    check_in = CheckIn(
        **check_in_data.model_dump(exclude_none=True)
    )

    db.add(check_in)

    room.status = "occupied"

    try:
        await db.commit()
        await db.refresh(check_in)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in data violates database constraints"
        )

    return check_in


async def update_check_in(
    db: AsyncSession,
    check_in_id: int,
    check_in_data: CheckInUpdate
) -> CheckIn:
    check_in = await get_check_in_by_id(db, check_in_id)

    update_data = check_in_data.model_dump(exclude_unset=True)

    new_check_in_time = update_data.get(
        "check_in_time",
        check_in.check_in_time
    )

    new_check_out_time = update_data.get(
        "check_out_time",
        check_in.check_out_time
    )

    if (
        new_check_in_time is not None
        and new_check_out_time is not None
        and new_check_out_time <= new_check_in_time
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="check_out_time must be later than check_in_time"
        )

    for field, value in update_data.items():
        setattr(check_in, field, value)

    try:
        await db.commit()
        await db.refresh(check_in)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in data violates database constraints"
        )

    return check_in


async def register_check_out(
    db: AsyncSession,
    check_in_id: int,
    check_out_time: datetime | None = None
) -> CheckIn:
    check_in = await get_check_in_by_id(db, check_in_id)

    if check_in.check_out_time is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out has already been registered"
        )

    if check_out_time is None:
        check_out_time = datetime.utcnow()

    if check_out_time <= check_in.check_in_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="check_out_time must be later than check_in_time"
        )

    check_in.check_out_time = check_out_time

    try:
        await db.commit()
        await db.refresh(check_in)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out data violates database constraints"
        )

    return check_in


async def delete_check_in(
    db: AsyncSession,
    check_in_id: int
) -> CheckIn:
    check_in = await get_check_in_by_id(db, check_in_id)

    try:
        await db.delete(check_in)
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in cannot be deleted because it has related records"
        )

    return check_in