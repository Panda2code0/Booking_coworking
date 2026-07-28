from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    return await auth_service.register_user(user_data, session)


@router.post(
    "/login",
    response_model=Token,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    credentials = UserLogin(
        username=form_data.username,
        password=form_data.password,
    )
    return await auth_service.login_user(credentials, session)
