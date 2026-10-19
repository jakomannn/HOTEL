from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CheckIn(Base):
    __tablename__ = "check_ins"

    check_in_id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.reservation_id"),
        nullable=False
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.employee_id"),
        nullable=False
    )

    check_in_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    check_out_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    reservation = relationship(
        "Reservation",
        back_populates="check_ins"
    )

    employee = relationship(
        "Employee"
    )

    stay_history = relationship(
        "StayHistory",
        back_populates="check_in",
        uselist=False
    )