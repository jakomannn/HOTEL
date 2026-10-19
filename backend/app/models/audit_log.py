from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_log_id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.employee_id", ondelete="SET NULL"),
        nullable=True
    )

    employee_role: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    action_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    table_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    record_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    old_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    new_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    request_ip: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    employee = relationship(
        "Employee"
    )