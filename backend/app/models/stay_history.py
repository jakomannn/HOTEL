from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StayHistory(Base):
    __tablename__ = "stay_history"

    history_id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    reservation_id: Mapped[int | None] = mapped_column(
        ForeignKey("reservations.reservation_id"),
        nullable=True
    )

    check_in_id: Mapped[int | None] = mapped_column(
        ForeignKey("check_ins.check_in_id"),
        nullable=True
    )

    client_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clients.client_id"),
        nullable=False
    )

    room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rooms.room_id"),
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

    total_nights: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    reservation = relationship(
        "Reservation",
        back_populates="stay_history"
    )

    check_in = relationship(
        "CheckIn",
        back_populates="stay_history"
    )

    client = relationship(
        "Client",
        back_populates="stay_history"
    )

    room = relationship(
        "Room",
        back_populates="stay_history"
    )