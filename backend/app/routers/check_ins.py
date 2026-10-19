from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_manager_with_audit
from app.database.session import get_db
from app.schemas.check_in import (
    CheckInCreate,
    CheckInUpdate,
    CheckInResponse,
    CheckOutRequest,
)
from app.services.check_in_service import (
    create_check_in,
    delete_check_in,
    get_check_in_by_id,
    get_check_ins,
    get_check_ins_by_employee,
    get_check_ins_by_reservation,
    register_check_out,
    update_check_in,
)


router = APIRouter(
    prefix="/check-ins",
    tags=["Check-ins"]
)


@router.post(
    "/",
    response_model=CheckInResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_check_in_endpoint(
    check_in_data: CheckInCreate,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await create_check_in(db, check_in_data)


@router.get(
    "/",
    response_model=list[CheckInResponse]
)
async def get_check_ins_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_check_ins(db, skip, limit)


@router.get(
    "/reservation/{reservation_id}",
    response_model=list[CheckInResponse]
)
async def get_check_ins_by_reservation_endpoint(
    reservation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_check_ins_by_reservation(
        db,
        reservation_id,
        skip,
        limit
    )


@router.get(
    "/employee/{employee_id}",
    response_model=list[CheckInResponse]
)
async def get_check_ins_by_employee_endpoint(
    employee_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_check_ins_by_employee(
        db,
        employee_id,
        skip,
        limit
    )


@router.get(
    "/{check_in_id}",
    response_model=CheckInResponse
)
async def get_check_in_endpoint(
    check_in_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await get_check_in_by_id(db, check_in_id)


@router.patch(
    "/{check_in_id}",
    response_model=CheckInResponse
)
async def update_check_in_endpoint(
    check_in_id: int,
    check_in_data: CheckInUpdate,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await update_check_in(
        db,
        check_in_id,
        check_in_data
    )


@router.patch(
    "/{check_in_id}/check-out",
    response_model=CheckInResponse
)
async def register_check_out_endpoint(
    check_in_id: int,
    check_out_data: CheckOutRequest | None = None,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    check_out_time = None

    if check_out_data is not None:
        check_out_time = check_out_data.check_out_time

    return await register_check_out(
        db=db,
        check_in_id=check_in_id,
        check_out_time=check_out_time
    )


@router.delete(
    "/{check_in_id}",
    response_model=CheckInResponse
)
async def delete_check_in_endpoint(
    check_in_id: int,
    db: AsyncSession = Depends(get_db),
    current_employee=Depends(require_manager_with_audit)
):
    return await delete_check_in(db, check_in_id)