from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_manager, require_manager_with_audit
from app.database.session import get_db
from app.schemas.reservation import (
    GuestReservationCreate,
    GuestReservationPublicResponse,
    GuestReservationsByPhoneRequest,
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
    ReservationWithPaymentResponse,
)
from app.schemas.room import RoomResponse
from app.services.reservation_service import (
    cancel_reservation,
    create_guest_reservation,
    create_reservation,
    delete_reservation,
    get_available_rooms,
    get_guest_reservations_by_phone,
    get_reservation_by_id,
    get_reservations,
    get_reservations_by_client,
    get_reservations_by_room,
    update_reservation,
)


router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"]
)


@router.post(
    "/",
    response_model=ReservationWithPaymentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_reservation_endpoint(
    reservation_data: ReservationCreate,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await create_reservation(db, reservation_data)


@router.post(
    "/guest",
    response_model=ReservationWithPaymentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_guest_reservation_endpoint(
    reservation_data: GuestReservationCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_guest_reservation(db, reservation_data)


@router.post(
    "/guest/by-phone",
    response_model=list[GuestReservationPublicResponse]
)
async def get_guest_reservations_by_phone_endpoint(
    request_data: GuestReservationsByPhoneRequest,
    db: AsyncSession = Depends(get_db)
):
    return await get_guest_reservations_by_phone(
        db=db,
        phone=request_data.phone
    )


@router.get(
    "/",
    response_model=list[ReservationResponse]
)
async def get_reservations_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager)
):
    return await get_reservations(db, skip, limit)


@router.get(
    "/available-rooms",
    response_model=list[RoomResponse]
)
async def get_available_rooms_endpoint(
    check_in_date: datetime,
    check_out_date: datetime,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await get_available_rooms(
        db=db,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        category_id=category_id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/client/{client_id}",
    response_model=list[ReservationResponse]
)
async def get_reservations_by_client_endpoint(
    client_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager)
):
    return await get_reservations_by_client(
        db,
        client_id,
        skip,
        limit
    )


@router.get(
    "/room/{room_id}",
    response_model=list[ReservationResponse]
)
async def get_reservations_by_room_endpoint(
    room_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager)
):
    return await get_reservations_by_room(
        db,
        room_id,
        skip,
        limit
    )


@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse
)
async def get_reservation_endpoint(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager)
):
    return await get_reservation_by_id(db, reservation_id)


@router.patch(
    "/{reservation_id}",
    response_model=ReservationResponse
)
async def update_reservation_endpoint(
    reservation_id: int,
    reservation_data: ReservationUpdate,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await update_reservation(
        db,
        reservation_id,
        reservation_data
    )


@router.patch(
    "/{reservation_id}/cancel",
    response_model=ReservationResponse
)
async def cancel_reservation_endpoint(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await cancel_reservation(db, reservation_id)


@router.delete(
    "/{reservation_id}",
    response_model=ReservationResponse
)
async def delete_reservation_endpoint(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await delete_reservation(db, reservation_id)