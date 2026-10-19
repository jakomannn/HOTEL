from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.models.payment import Payment
from app.models.reservation import Reservation
from app.models.room import Room
from app.schemas.reservation import (
    GuestReservationCreate,
    GuestReservationPublicResponse,
    ReservationCreate,
    ReservationUpdate,
)
from app.services.client_service import get_client_by_id, get_or_create_client
from app.services.employee_service import get_employee_by_id
from app.services.room_category_service import get_room_category_by_id
from app.services.room_service import get_room_by_id


ACTIVE_RESERVATION_STATUSES = ["pending", "confirmed"]
SYSTEM_EMPLOYEE_ID = 0


def get_guest_reservation_display_status(
    reservation: Reservation,
    payment: Payment | None
) -> str:
    if reservation.status == "cancelled":
        return "Бронь отменена"

    if reservation.status == "completed":
        return "Проживание завершено"

    if reservation.status == "checked_in":
        return "Гость заселён"

    if payment is None:
        return "Ожидает формирования оплаты"

    if payment.status == "pending":
        return "Ожидает оплаты"

    if payment.status == "paid":
        return "Бронь оплачена"

    if payment.status == "failed":
        return "Оплата не прошла"

    if reservation.status == "confirmed":
        return "Бронь подтверждена"

    return "Бронь создана"


def can_guest_pay(
    reservation: Reservation,
    payment: Payment | None
) -> bool:
    if payment is None:
        return False

    if reservation.status in {"cancelled", "completed", "checked_in"}:
        return False

    return payment.status in {"pending", "failed"}


async def get_reservation_by_id(
    db: AsyncSession,
    reservation_id: int
) -> Reservation:
    result = await db.execute(
        select(Reservation).where(
            Reservation.reservation_id == reservation_id
        )
    )

    reservation = result.scalar_one_or_none()

    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )

    return reservation


async def get_reservations(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Reservation]:
    result = await db.execute(
        select(Reservation)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_reservations_by_client(
    db: AsyncSession,
    client_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[Reservation]:
    await get_client_by_id(db, client_id)

    result = await db.execute(
        select(Reservation)
        .where(Reservation.client_id == client_id)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_reservations_by_room(
    db: AsyncSession,
    room_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[Reservation]:
    await get_room_by_id(db, room_id)

    result = await db.execute(
        select(Reservation)
        .where(Reservation.room_id == room_id)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_guest_reservations_by_phone(
    db: AsyncSession,
    phone: str
) -> list[GuestReservationPublicResponse]:
    normalized_phone = phone.strip()

    result = await db.execute(
        select(
            Reservation,
            Room,
            Payment
        )
        .join(
            Client,
            Client.client_id == Reservation.client_id
        )
        .join(
            Room,
            Room.room_id == Reservation.room_id
        )
        .outerjoin(
            Payment,
            Payment.reservation_id == Reservation.reservation_id
        )
        .where(Client.phone == normalized_phone)
        .order_by(Reservation.check_in_date.desc())
    )

    rows = result.all()

    reservations: list[GuestReservationPublicResponse] = []

    for reservation, room, payment in rows:
        reservations.append(
            GuestReservationPublicResponse(
                reservation_id=reservation.reservation_id,
                room_number=room.room_number,
                check_in_date=reservation.check_in_date,
                check_out_date=reservation.check_out_date,
                amount=payment.amount if payment is not None else None,
                payment_id=payment.payment_id if payment is not None else None,
                can_pay=can_guest_pay(reservation, payment),
                display_status=get_guest_reservation_display_status(
                    reservation,
                    payment
                )
            )
        )

    return reservations


async def check_room_availability(
    db: AsyncSession,
    room_id: int,
    check_in_date: datetime,
    check_out_date: datetime,
    exclude_reservation_id: int | None = None
) -> bool:
    query = select(Reservation).where(
        Reservation.room_id == room_id,
        Reservation.status.in_(ACTIVE_RESERVATION_STATUSES),
        Reservation.check_in_date < check_out_date,
        Reservation.check_out_date > check_in_date
    )

    if exclude_reservation_id is not None:
        query = query.where(
            Reservation.reservation_id != exclude_reservation_id
        )

    result = await db.execute(query)
    conflicting_reservation = result.scalar_one_or_none()

    return conflicting_reservation is None


async def get_available_rooms(
    db: AsyncSession,
    check_in_date: datetime,
    check_out_date: datetime,
    category_id: int | None = None,
    skip: int = 0,
    limit: int = 100
) -> list[Room]:
    if check_out_date <= check_in_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="check_out_date must be later than check_in_date"
        )

    if category_id is not None:
        await get_room_category_by_id(db, category_id)

    conflicting_rooms_subquery = (
        select(Reservation.room_id)
        .where(
            Reservation.status.in_(ACTIVE_RESERVATION_STATUSES),
            Reservation.check_in_date < check_out_date,
            Reservation.check_out_date > check_in_date
        )
    )

    query = (
        select(Room)
        .where(Room.room_id.not_in(conflicting_rooms_subquery))
        .offset(skip)
        .limit(limit)
    )

    if category_id is not None:
        query = query.where(Room.category_id == category_id)

    result = await db.execute(query)

    return list(result.scalars().all())


async def get_payment_by_reservation_id(
    db: AsyncSession,
    reservation_id: int
) -> Payment:
    result = await db.execute(
        select(Payment).where(
            Payment.reservation_id == reservation_id
        )
    )

    payment = result.scalar_one_or_none()

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment was not created by database trigger"
        )

    return payment


async def create_reservation(
    db: AsyncSession,
    reservation_data: ReservationCreate
) -> dict:
    await get_client_by_id(db, reservation_data.client_id)
    await get_room_by_id(db, reservation_data.room_id)
    await get_employee_by_id(db, reservation_data.employee_id)

    is_available = await check_room_availability(
        db=db,
        room_id=reservation_data.room_id,
        check_in_date=reservation_data.check_in_date,
        check_out_date=reservation_data.check_out_date
    )

    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is not available for selected dates"
        )

    reservation = Reservation(
        **reservation_data.model_dump()
    )

    db.add(reservation)

    try:
        await db.flush()

        payment = await get_payment_by_reservation_id(
            db=db,
            reservation_id=reservation.reservation_id
        )

        await db.commit()
        await db.refresh(reservation)
        await db.refresh(payment)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation data violates database constraints"
        )

    return {
        "reservation": reservation,
        "payment": payment
    }


async def create_guest_reservation(
    db: AsyncSession,
    reservation_data: GuestReservationCreate
) -> dict:
    await get_employee_by_id(db, SYSTEM_EMPLOYEE_ID)
    await get_room_by_id(db, reservation_data.room_id)

    is_available = await check_room_availability(
        db=db,
        room_id=reservation_data.room_id,
        check_in_date=reservation_data.check_in_date,
        check_out_date=reservation_data.check_out_date
    )

    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is not available for selected dates"
        )

    try:
        client = await get_or_create_client(
            db=db,
            first_name=reservation_data.first_name,
            last_name=reservation_data.last_name,
            email=reservation_data.email,
            phone=reservation_data.phone,
            passport_number=reservation_data.passport_number
        )

        reservation = Reservation(
            client_id=client.client_id,
            room_id=reservation_data.room_id,
            employee_id=SYSTEM_EMPLOYEE_ID,
            check_in_date=reservation_data.check_in_date,
            check_out_date=reservation_data.check_out_date,
            status="pending"
        )

        db.add(reservation)
        await db.flush()

        payment = await get_payment_by_reservation_id(
            db=db,
            reservation_id=reservation.reservation_id
        )

        await db.commit()
        await db.refresh(reservation)
        await db.refresh(payment)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest reservation data violates database constraints"
        )

    return {
        "reservation": reservation,
        "payment": payment
    }


async def update_reservation(
    db: AsyncSession,
    reservation_id: int,
    reservation_data: ReservationUpdate
) -> Reservation:
    reservation = await get_reservation_by_id(db, reservation_id)

    update_data = reservation_data.model_dump(exclude_unset=True)

    if "client_id" in update_data:
        await get_client_by_id(db, update_data["client_id"])

    if "room_id" in update_data:
        await get_room_by_id(db, update_data["room_id"])

    if "employee_id" in update_data:
        await get_employee_by_id(db, update_data["employee_id"])

    new_room_id = update_data.get("room_id", reservation.room_id)
    new_check_in_date = update_data.get(
        "check_in_date",
        reservation.check_in_date
    )
    new_check_out_date = update_data.get(
        "check_out_date",
        reservation.check_out_date
    )

    if new_check_out_date <= new_check_in_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="check_out_date must be later than check_in_date"
        )

    is_available = await check_room_availability(
        db=db,
        room_id=new_room_id,
        check_in_date=new_check_in_date,
        check_out_date=new_check_out_date,
        exclude_reservation_id=reservation_id
    )

    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is not available for selected dates"
        )

    for field, value in update_data.items():
        setattr(reservation, field, value)

    try:
        await db.commit()
        await db.refresh(reservation)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation data violates database constraints"
        )

    return reservation


async def cancel_reservation(
    db: AsyncSession,
    reservation_id: int
) -> Reservation:
    reservation = await get_reservation_by_id(db, reservation_id)

    if reservation.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completed reservation cannot be cancelled"
        )

    reservation.status = "cancelled"

    try:
        await db.commit()
        await db.refresh(reservation)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation cannot be cancelled"
        )

    return reservation


async def delete_reservation(
    db: AsyncSession,
    reservation_id: int
) -> Reservation:
    reservation = await get_reservation_by_id(db, reservation_id)

    try:
        await db.delete(reservation)
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation cannot be deleted because it has related records"
        )

    return reservation