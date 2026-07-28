from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.time_slot import (
    TimeSlotCreate,
    TimeSlotResponse,
    TimeSlotUpdate,
)
from app.services import slot_service

router = APIRouter(
    prefix="/slots",
    tags=["Time Slots"],
)


@router.post(
    "/",
    response_model=TimeSlotResponse,
    status_code=201,
)
async def create_slot(
    slot: TimeSlotCreate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    return await slot_service.create_slot(
        slot,
        session,
    )


@router.get(
    "/",
    response_model=list[TimeSlotResponse],
)
async def get_slots(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return await slot_service.get_slots(session)


@router.get(
    "/{slot_id}",
    response_model=TimeSlotResponse,
)
async def get_slot(
    slot_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return await slot_service.get_slot(
        slot_id,
        session,
    )


@router.patch(
    "/{slot_id}",
    response_model=TimeSlotResponse,
)
async def update_slot(
    slot_id: int,
    slot: TimeSlotUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    return await slot_service.update_slot(
        slot_id,
        slot,
        session,
    )


@router.delete(
    "/{slot_id}",
    status_code=204,
)
async def delete_slot(
    slot_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    await slot_service.delete_slot(
        slot_id,
        session,
    )

    return Response(status_code=204)
