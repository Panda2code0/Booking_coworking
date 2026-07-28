from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    capacity: Mapped[int]

    time_slots: Mapped[list["TimeSlot"]] = relationship(
        back_populates="room",
    )
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="room",
    )