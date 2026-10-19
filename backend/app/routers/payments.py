from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_manager_with_audit
from app.database.session import get_db
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from app.services.payment_service import (
    create_payment,
    delete_payment,
    get_payment_by_id,
    get_payments,
    get_payments_by_reservation,
    mark_payment_as_failed,
    mark_payment_as_paid,
    update_payment,
)


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_payment_endpoint(
    payment_data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await create_payment(db, payment_data)


@router.get(
    "/",
    response_model=list[PaymentResponse]
)
async def get_payments_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_payments(db, skip, limit)


@router.get(
    "/reservation/{reservation_id}",
    response_model=list[PaymentResponse]
)
async def get_payments_by_reservation_endpoint(
    reservation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_payments_by_reservation(
        db,
        reservation_id,
        skip,
        limit
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse
)
async def get_payment_endpoint(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_payment_by_id(db, payment_id)


@router.patch(
    "/{payment_id}",
    response_model=PaymentResponse
)
async def update_payment_endpoint(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await update_payment(db, payment_id, payment_data)


@router.patch(
    "/{payment_id}/paid",
    response_model=PaymentResponse
)
async def mark_payment_as_paid_endpoint(
    payment_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await mark_payment_as_paid(db, payment_id)


@router.patch(
    "/{payment_id}/failed",
    response_model=PaymentResponse
)
async def mark_payment_as_failed_endpoint(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await mark_payment_as_failed(db, payment_id)


@router.delete(
    "/{payment_id}",
    response_model=PaymentResponse
)
async def delete_payment_endpoint(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await delete_payment(db, payment_id)