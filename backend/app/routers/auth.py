from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth.dependencies import get_current_employee, get_employee_role
from app.auth.jwt_handler import create_access_token
from app.auth.password import verify_password
from app.database.session import get_db
from app.models.employee import Employee
from app.schemas.auth import TokenResponse


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/login",
    response_model=TokenResponse
)
async def login_employee(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Employee)
        .options(joinedload(Employee.position))
        .where(Employee.email == form_data.username)
    )

    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not verify_password(
        form_data.password,
        employee.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if employee.status is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive employee"
        )

    role = get_employee_role(employee)

    access_token = create_access_token(
        data={
            "sub": str(employee.employee_id),
            "employee_id": employee.employee_id,
            "role": role
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


@router.get("/me")
async def get_me(
    current_employee: Employee = Depends(get_current_employee)
):
    return {
        "employee_id": current_employee.employee_id,
        "first_name": current_employee.first_name,
        "last_name": current_employee.last_name,
        "email": current_employee.email,
        "phone": current_employee.phone,
        "position_id": current_employee.position_id,
        "role": get_employee_role(current_employee),
        "status": current_employee.status
    }