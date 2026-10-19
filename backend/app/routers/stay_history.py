from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_manager_with_audit
from app.database.session import get_db
from app.schemas.stay_history import StayHistoryResponse
from app.services.stay_history_service import (
    get_stay_history_by_check_in,
    get_stay_history_by_client,
    get_stay_history_by_id,
    get_stay_history_by_reservation,
    get_stay_history_by_room,
    get_stay_history_records,
)


router = APIRouter(
    prefix="/stay-history",
    tags=["Stay History"]
)


@router.get(
    "/",
    response_model=list[StayHistoryResponse]
)
async def get_stay_history_records_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_stay_history_records(db, skip, limit)


@router.get(
    "/client/{client_id}",
    response_model=list[StayHistoryResponse]
)
async def get_stay_history_by_client_endpoint(
    client_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_stay_history_by_client(
        db,
        client_id,
        skip,
        limit
    )


@router.get(
    "/room/{room_id}",
    response_model=list[StayHistoryResponse]
)
async def get_stay_history_by_room_endpoint(
    room_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_stay_history_by_room(
        db,
        room_id,
        skip,
        limit
    )


@router.get(
    "/reservation/{reservation_id}",
    response_model=StayHistoryResponse
)
async def get_stay_history_by_reservation_endpoint(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_stay_history_by_reservation(
        db,
        reservation_id
    )


@router.get(
    "/check-in/{check_in_id}",
    response_model=StayHistoryResponse
)
async def get_stay_history_by_check_in_endpoint(
    check_in_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_stay_history_by_check_in(
        db,
        check_in_id
    )


@router.get(
    "/{history_id}",
    response_model=StayHistoryResponse
)
async def get_stay_history_endpoint(
    history_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_stay_history_by_id(db, history_id)