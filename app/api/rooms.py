from datetime import date

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.room import (
    RoomAvailability,
    RoomCreate,
    RoomResponse,
    RoomUpdate,
)
from app.services import room_service

router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
)


@router.post(
    "/",
    response_model=RoomResponse,
    status_code=201,
)
async def create_room(
    room: RoomCreate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    return await room_service.create_room(
        room,
        session,
    )


@router.get(
    "/",
    response_model=list[RoomResponse],
)
async def get_rooms(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return await room_service.get_rooms(session)


@router.get(
    "/availability",
    response_model=list[RoomAvailability],
)
async def get_rooms_availability(
    target_date: date = Query(..., alias="date", description="Дата для просмотра занятости"),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return await room_service.get_rooms_availability(
        target_date,
        session,
    )


@router.get(
    "/{room_id}",
    response_model=RoomResponse,
)
async def get_room(
    room_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return await room_service.get_room(
        room_id,
        session,
    )


@router.patch(
    "/{room_id}",
    response_model=RoomResponse,
)
async def update_room(
    room_id: int,
    room: RoomUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    return await room_service.update_room(
        room_id,
        room,
        session,
    )


@router.delete(
    "/{room_id}",
    status_code=204,
)
async def delete_room(
    room_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    await room_service.delete_room(
        room_id,
        session,
    )

    return Response(status_code=204)
