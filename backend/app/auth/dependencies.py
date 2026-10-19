from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth.jwt_handler import decode_access_token
from app.auth.roles import is_admin, is_employee, is_manager
from app.database.session import get_db
from app.models.employee import Employee


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


async def get_current_employee(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Employee:
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    employee_id = payload.get("employee_id")

    if employee_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )

    result = await db.execute(
        select(Employee)
        .options(joinedload(Employee.position))
        .where(Employee.employee_id == int(employee_id))
    )

    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employee not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if employee.status is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive employee"
        )

    return employee


def get_employee_role(employee: Employee) -> str:
    if employee.position is None:
        return ""

    return employee.position.name.lower()


async def set_audit_context(
    db: AsyncSession,
    employee: Employee,
    request: Request
) -> None:
    role = get_employee_role(employee)
    request_ip = request.client.host if request.client else ""

    await db.execute(
        text("""
            SELECT
                set_config('app.employee_id', :employee_id, true),
                set_config('app.employee_role', :employee_role, true),
                set_config('app.request_ip', :request_ip, true)
        """),
        {
            "employee_id": str(employee.employee_id),
            "employee_role": role,
            "request_ip": request_ip
        }
    )


async def require_employee(
    current_employee: Employee = Depends(get_current_employee)
) -> Employee:
    role = get_employee_role(current_employee)

    if not is_employee(role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required"
        )

    return current_employee


async def require_admin(
    current_employee: Employee = Depends(get_current_employee)
) -> Employee:
    role = get_employee_role(current_employee)

    if not is_admin(role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_employee


async def require_manager(
    current_employee: Employee = Depends(get_current_employee)
) -> Employee:
    role = get_employee_role(current_employee)

    if not is_manager(role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    return current_employee


async def require_employee_with_audit(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee)
) -> Employee:
    role = get_employee_role(current_employee)

    if not is_employee(role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required"
        )

    await set_audit_context(
        db=db,
        employee=current_employee,
        request=request
    )

    return current_employee


async def require_admin_with_audit(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee)
) -> Employee:
    role = get_employee_role(current_employee)

    if not is_admin(role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    await set_audit_context(
        db=db,
        employee=current_employee,
        request=request
    )

    return current_employee


async def require_manager_with_audit(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee)
) -> Employee:
    role = get_employee_role(current_employee)

    if not is_manager(role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    await set_audit_context(
        db=db,
        employee=current_employee,
        request=request
    )

    return current_employee