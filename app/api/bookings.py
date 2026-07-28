from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.services import booking_service

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=201,
)
async def create_booking(
    booking: BookingCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await booking_service.create_booking(
        booking,
        current_user,
        session,
    )


@router.get(
    "/me",
    response_model=list[BookingResponse],
)
async def get_my_bookings(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await booking_service.get_user_bookings(
        current_user,
        session,
    )


@router.get(
    "/",
    response_model=list[BookingResponse],
)
async def get_all_bookings(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    return await booking_service.get_all_bookings(session)


@router.delete(
    "/{booking_id}",
    status_code=204,
)
async def cancel_or_delete_booking(
    booking_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await booking_service.cancel_or_delete_booking(
        booking_id,
        current_user,
        session,
    )
    return Response(status_code=204)
