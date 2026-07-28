from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin


async def register_user(
    user_data: UserCreate,
    session: AsyncSession,
) -> User:
    db_user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        role=UserRole.EMPLOYEE,
    )

    session.add(db_user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким именем уже существует.",
        )

    await session.refresh(db_user)
    return db_user


async def authenticate_user(
    credentials: UserLogin,
    session: AsyncSession,
) -> User:
    result = await session.execute(
        select(User).where(User.username == credentials.username),
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(
        credentials.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def login_user(
    credentials: UserLogin,
    session: AsyncSession,
) -> dict:
    user = await authenticate_user(credentials, session)
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
