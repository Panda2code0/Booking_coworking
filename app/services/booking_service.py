from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.enums import UserRole
from app.models.room import Room
from app.models.time_slot import TimeSlot
from app.models.user import User
from app.schemas.booking import BookingCreate


async def create_booking(
    booking_data: BookingCreate,
    user: User,
    session: AsyncSession,
) -> Booking:
    room = await session.get(Room, booking_data.room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комната не найдена.",
        )

    time_slot = await session.get(TimeSlot, booking_data.time_slot_id)
    if time_slot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Слот не найден.",
        )

    if time_slot.room_id != booking_data.room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Слот не принадлежит указанной комнате.",
        )

    db_booking = Booking(
        room_id=booking_data.room_id,
        user_id=user.id,
        date=booking_data.date,
        time_slot_id=booking_data.time_slot_id,
    )

    session.add(db_booking)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Комната уже забронирована на эту дату и время.",
        )

    await session.refresh(db_booking)
    return db_booking


async def get_user_bookings(
    user: User,
    session: AsyncSession,
) -> list[Booking]:
    result = await session.execute(
        select(Booking).where(Booking.user_id == user.id),
    )
    return list(result.scalars().all())


async def get_all_bookings(
    session: AsyncSession,
) -> list[Booking]:
    result = await session.execute(select(Booking))
    return list(result.scalars().all())


async def get_booking(
    booking_id: int,
    session: AsyncSession,
) -> Booking:
    booking = await session.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено.",
        )
    return booking


async def cancel_or_delete_booking(
    booking_id: int,
    user: User,
    session: AsyncSession,
) -> None:
    booking = await get_booking(booking_id, session)

    if user.role == UserRole.ADMIN or booking.user_id == user.id:
        await session.delete(booking)
        await session.commit()
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав для отмены бронирования.",
    )
