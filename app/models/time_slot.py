from datetime import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(primary_key=True)

    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"),
    )

    start_time: Mapped[time]

    end_time: Mapped[time]

    room: Mapped["Room"] = relationship(
        back_populates="time_slots",
    )
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="time_slot",
    )