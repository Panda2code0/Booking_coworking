from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.time_slot import TimeSlot
from app.schemas.time_slot import TimeSlotCreate, TimeSlotUpdate


async def create_slot(
    slot_data: TimeSlotCreate,
    session: AsyncSession,
) -> TimeSlot:
    db_slot = TimeSlot(
        room_id=slot_data.room_id,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time,
    )

    session.add(db_slot)

    try:
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Комната не существует.",
        )

    await session.refresh(db_slot)

    return db_slot


async def get_slots(
    session: AsyncSession,
) -> list[TimeSlot]:
    result = await session.execute(select(TimeSlot))
    return result.scalars().all()


async def get_slot(
    slot_id: int,
    session: AsyncSession,
) -> TimeSlot:
    result = await session.execute(
        select(TimeSlot).where(TimeSlot.id == slot_id)
    )

    slot = result.scalar_one_or_none()

    if slot is None:
        raise HTTPException(
            status_code=404,
            detail="Слот не найден.",
        )

    return slot


async def update_slot(
    slot_id: int,
    slot_data: TimeSlotUpdate,
    session: AsyncSession,
) -> TimeSlot:
    slot = await get_slot(slot_id, session)

    update_data = slot_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(slot, field, value)

    try:
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Ошибка обновления слота.",
        )

    await session.refresh(slot)

    return slot


async def delete_slot(
    slot_id: int,
    session: AsyncSession,
) -> None:
    slot = await get_slot(slot_id, session)

    await session.delete(slot)
    await session.commit()