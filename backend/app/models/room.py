from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    room_id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    room_number: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False
    )

    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("room_categories.category_id"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="free",
        nullable=False
    )

    category = relationship(
        "RoomCategory",
        back_populates="rooms"
    )

    reservations = relationship(
        "Reservation",
        back_populates="room"
    )

    stay_history = relationship(
        "StayHistory",
        back_populates="room"
    )