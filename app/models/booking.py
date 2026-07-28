from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "date",
            "time_slot_id",
            name="uq_room_date_slot",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    date: Mapped[date] = mapped_column(Date)

    time_slot_id: Mapped[int] = mapped_column(
        ForeignKey("time_slots.id"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    room: Mapped["Room"] = relationship(
        back_populates="bookings",
    )
    user: Mapped["User"] = relationship(
        back_populates="bookings",
    )
    time_slot: Mapped["TimeSlot"] = relationship(
        back_populates="bookings",
    )
