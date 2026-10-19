from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.client_id"),
        nullable=False
    )

    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.room_id"),
        nullable=False
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.employee_id"),
        nullable=False
    )

    check_in_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    check_out_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    client = relationship(
        "Client",
        back_populates="reservations"
    )

    room = relationship(
        "Room",
        back_populates="reservations"
    )

    payments = relationship(
        "Payment",
        back_populates="reservation"
    )

    check_ins = relationship(
        "CheckIn",
        back_populates="reservation"
    )

    stay_history = relationship(
        "StayHistory",
        back_populates="reservation",
        uselist=False
    )