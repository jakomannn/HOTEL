from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.services.reservation_service import get_reservation_by_id


async def get_payment_by_id(
    db: AsyncSession,
    payment_id: int
) -> Payment:
    result = await db.execute(
        select(Payment).where(Payment.payment_id == payment_id)
    )

    payment = result.scalar_one_or_none()

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return payment


async def get_payments(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Payment]:
    result = await db.execute(
        select(Payment)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_payments_by_reservation(
    db: AsyncSession,
    reservation_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[Payment]:
    await get_reservation_by_id(db, reservation_id)

    result = await db.execute(
        select(Payment)
        .where(Payment.reservation_id == reservation_id)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def create_payment(
    db: AsyncSession,
    payment_data: PaymentCreate
) -> Payment:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Manual payment creation is disabled. Payment is created automatically by database trigger after reservation creation."
    )


async def update_payment(
    db: AsyncSession,
    payment_id: int,
    payment_data: PaymentUpdate
) -> Payment:
    payment = await get_payment_by_id(db, payment_id)

    update_data = payment_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(payment, field, value)

    try:
        await db.commit()
        await db.refresh(payment)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment data violates database constraints"
        )

    return payment


async def mark_payment_as_paid(
    db: AsyncSession,
    payment_id: int
) -> Payment:
    payment = await get_payment_by_id(db, payment_id)

    if payment.status == "paid":
        return payment

    if payment.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed payment cannot be marked as paid"
        )

    payment.status = "paid"

    try:
        await db.commit()
        await db.refresh(payment)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment cannot be marked as paid"
        )

    return payment


async def mark_payment_as_failed(
    db: AsyncSession,
    payment_id: int
) -> Payment:
    payment = await get_payment_by_id(db, payment_id)

    if payment.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paid payment cannot be marked as failed"
        )

    payment.status = "failed"

    try:
        await db.commit()
        await db.refresh(payment)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment cannot be marked as failed"
        )

    return payment


async def delete_payment(
    db: AsyncSession,
    payment_id: int
) -> Payment:
    payment = await get_payment_by_id(db, payment_id)

    try:
        await db.delete(payment)
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment cannot be deleted because it has related records"
        )

    return payment