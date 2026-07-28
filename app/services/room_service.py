from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.room import Room
from app.models.time_slot import TimeSlot
from app.schemas.room import (
    RoomAvailability,
    RoomCreate,
    RoomUpdate,
    SlotAvailability,
)


async def create_room(
    room_data: RoomCreate,
    session: AsyncSession,
) -> Room:
    db_room = Room(
        name=room_data.name,
        capacity=room_data.capacity,
    )

    session.add(db_room)

    try:
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Комната с таким названием уже существует.",
        )

    await session.refresh(db_room)

    return db_room


async def get_rooms(
    session: AsyncSession,
) -> list[Room]:
    result = await session.execute(select(Room))
    return result.scalars().all()


async def get_room(
    room_id: int,
    session: AsyncSession,
) -> Room:
    result = await session.execute(
        select(Room).where(Room.id == room_id)
    )

    room = result.scalar_one_or_none()

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Комната не найдена.",
        )

    return room


async def get_rooms_availability(
    target_date: date,
    session: AsyncSession,
) -> list[RoomAvailability]:
    rooms_result = await session.execute(select(Room).order_by(Room.id))
    rooms = list(rooms_result.scalars().all())

    slots_result = await session.execute(
        select(TimeSlot).order_by(TimeSlot.room_id, TimeSlot.start_time),
    )
    slots = list(slots_result.scalars().all())

    bookings_result = await session.execute(
        select(Booking).where(Booking.date == target_date),
    )
    bookings = list(bookings_result.scalars().all())

    booked_slot_ids = {booking.time_slot_id for booking in bookings}
    slots_by_room: dict[int, list[TimeSlot]] = {}
    for slot in slots:
        slots_by_room.setdefault(slot.room_id, []).append(slot)

    availability: list[RoomAvailability] = []
    for room in rooms:
        room_slots = slots_by_room.get(room.id, [])
        availability.append(
            RoomAvailability(
                room_id=room.id,
                room_name=room.name,
                capacity=room.capacity,
                date=target_date,
                slots=[
                    SlotAvailability(
                        slot_id=slot.id,
                        start_time=slot.start_time,
                        end_time=slot.end_time,
                        is_available=slot.id not in booked_slot_ids,
                    )
                    for slot in room_slots
                ],
            ),
        )

    return availability


async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    session: AsyncSession,
) -> Room:
    room = await get_room(room_id, session)

    update_data = room_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(room, field, value)

    try:
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Комната с таким названием уже существует.",
        )

    await session.refresh(room)

    return room


async def delete_room(
    room_id: int,
    session: AsyncSession,
) -> None:
    room = await get_room(room_id, session)

    await session.delete(room)
    await session.commit()
