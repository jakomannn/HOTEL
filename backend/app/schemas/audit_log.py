from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    audit_log_id: int

    employee_id: int | None
    employee_role: str | None

    action_type: str
    table_name: str
    record_id: str | None

    old_data: dict | None
    new_data: dict | None

    request_ip: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)