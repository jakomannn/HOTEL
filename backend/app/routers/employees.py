from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin, require_admin_with_audit
from app.database.session import get_db
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services.employee_service import (
    create_employee,
    delete_employee,
    get_employee_by_id,
    get_employees,
    update_employee,
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_employee_endpoint(
    employee_data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await create_employee(db, employee_data)


@router.get(
    "/",
    response_model=list[EmployeeResponse]
)
async def get_employees_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin)
):
    return await get_employees(db, skip, limit)


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
async def get_employee_endpoint(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin)
):
    return await get_employee_by_id(db, employee_id)


@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse
)
async def update_employee_endpoint(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await update_employee(db, employee_id, employee_data)


@router.delete(
    "/{employee_id}",
    response_model=EmployeeResponse
)
async def delete_employee_endpoint(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin_with_audit)
):
    return await delete_employee(db, employee_id)