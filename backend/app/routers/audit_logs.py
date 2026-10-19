from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogResponse


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.get(
    "/",
    response_model=list[AuditLogResponse]
)
async def get_audit_logs(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    employee_id: int | None = None,
    table_name: str | None = None,
    action_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_admin),
):
    query = select(AuditLog)

    if employee_id is not None:
        query = query.where(AuditLog.employee_id == employee_id)

    if table_name is not None:
        query = query.where(AuditLog.table_name == table_name)

    if action_type is not None:
        query = query.where(AuditLog.action_type == action_type.upper())

    query = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)

    return list(result.scalars().all())