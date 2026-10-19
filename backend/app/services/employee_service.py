from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.password import hash_password
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.services.position_service import get_position_by_id


async def get_employee_by_id(
    db: AsyncSession,
    employee_id: int
) -> Employee:
    result = await db.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )

    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return employee


async def get_employees(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Employee]:
    result = await db.execute(
        select(Employee)
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


async def get_employee_by_email(
    db: AsyncSession,
    email: str
) -> Employee | None:
    result = await db.execute(
        select(Employee).where(Employee.email == email)
    )

    return result.scalar_one_or_none()


async def get_employee_by_phone(
    db: AsyncSession,
    phone: str
) -> Employee | None:
    result = await db.execute(
        select(Employee).where(Employee.phone == phone)
    )

    return result.scalar_one_or_none()


async def create_employee(
    db: AsyncSession,
    employee_data: EmployeeCreate
) -> Employee:
    await get_position_by_id(db, employee_data.position_id)

    existing_email = await get_employee_by_email(
        db,
        employee_data.email
    )

    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this email already exists"
        )

    existing_phone = await get_employee_by_phone(
        db,
        employee_data.phone
    )

    if existing_phone is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this phone already exists"
        )

    employee_dict = employee_data.model_dump(
        exclude={"password"}
    )

    employee = Employee(
        **employee_dict,
        hashed_password=hash_password(employee_data.password)
    )

    db.add(employee)

    try:
        await db.commit()
        await db.refresh(employee)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee data violates database constraints"
        )

    return employee


async def update_employee(
    db: AsyncSession,
    employee_id: int,
    employee_data: EmployeeUpdate
) -> Employee:
    employee = await get_employee_by_id(db, employee_id)

    update_data = employee_data.model_dump(exclude_unset=True)

    if "position_id" in update_data:
        await get_position_by_id(db, update_data["position_id"])

    if "email" in update_data:
        existing_email = await get_employee_by_email(
            db,
            update_data["email"]
        )

        if (
            existing_email is not None
            and existing_email.employee_id != employee_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee with this email already exists"
            )

    if "phone" in update_data:
        existing_phone = await get_employee_by_phone(
            db,
            update_data["phone"]
        )

        if (
            existing_phone is not None
            and existing_phone.employee_id != employee_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee with this phone already exists"
            )

    if "password" in update_data:
        password = update_data.pop("password")
        employee.hashed_password = hash_password(password)

    for field, value in update_data.items():
        setattr(employee, field, value)

    try:
        await db.commit()
        await db.refresh(employee)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee data violates database constraints"
        )

    return employee


async def delete_employee(
    db: AsyncSession,
    employee_id: int
) -> Employee:
    employee = await get_employee_by_id(db, employee_id)

    try:
        await db.delete(employee)
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee cannot be deleted because it has related records"
        )

    return employee