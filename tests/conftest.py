"""Pytest configuration and shared fixtures."""

import asyncio
import os
from collections.abc import AsyncGenerator, Callable
from datetime import date, time

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "meeting_booking_test")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "postgres")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from app.core.config import settings  # noqa: E402
from app.core.security import create_access_token, hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Booking, Room, TimeSlot, User  # noqa: E402
from app.models.enums import UserRole  # noqa: E402

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)


async def _ensure_test_database() -> None:
    conn = await asyncpg.connect(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database="postgres",
    )
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            settings.DB_NAME,
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{settings.DB_NAME}"')
    finally:
        await conn.close()


@pytest.fixture(scope="session", autouse=True)
def initialize_test_database() -> None:
    asyncio.run(_ensure_test_database())


@pytest.fixture
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory(test_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> Callable[[str], dict[str, str]]:
    def _make_headers(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    return _make_headers


@pytest.fixture
def user_credentials() -> dict[str, str]:
    return {"username": "employee", "password": "employee_pass"}


@pytest.fixture
def admin_credentials() -> dict[str, str]:
    return {"username": "admin", "password": "admin_pass"}


@pytest.fixture
async def regular_user(
    db_session: AsyncSession,
    user_credentials: dict[str, str],
) -> User:
    user = User(
        username=user_credentials["username"],
        password_hash=hash_password(user_credentials["password"]),
        role=UserRole.EMPLOYEE,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(
    db_session: AsyncSession,
    admin_credentials: dict[str, str],
) -> User:
    user = User(
        username=admin_credentials["username"],
        password_hash=hash_password(admin_credentials["password"]),
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def other_user(db_session: AsyncSession) -> User:
    user = User(
        username="other_user",
        password_hash=hash_password("other_pass"),
        role=UserRole.EMPLOYEE,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def user_token(regular_user: User) -> str:
    return create_access_token(data={"sub": regular_user.username})


@pytest.fixture
def admin_token(admin_user: User) -> str:
    return create_access_token(data={"sub": admin_user.username})


@pytest.fixture
def other_user_token(other_user: User) -> str:
    return create_access_token(data={"sub": other_user.username})


@pytest.fixture
def user_auth_headers(user_token: str, auth_headers) -> dict[str, str]:
    return auth_headers(user_token)


@pytest.fixture
def admin_auth_headers(admin_token: str, auth_headers) -> dict[str, str]:
    return auth_headers(admin_token)


@pytest.fixture
def other_user_auth_headers(other_user_token: str, auth_headers) -> dict[str, str]:
    return auth_headers(other_user_token)


@pytest.fixture
async def room(db_session: AsyncSession) -> Room:
    db_room = Room(name="Conference A", capacity=10)
    db_session.add(db_room)
    await db_session.commit()
    await db_session.refresh(db_room)
    return db_room


@pytest.fixture
async def another_room(db_session: AsyncSession) -> Room:
    db_room = Room(name="Conference B", capacity=5)
    db_session.add(db_room)
    await db_session.commit()
    await db_session.refresh(db_room)
    return db_room


@pytest.fixture
async def time_slot(db_session: AsyncSession, room: Room) -> TimeSlot:
    slot = TimeSlot(
        room_id=room.id,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    db_session.add(slot)
    await db_session.commit()
    await db_session.refresh(slot)
    return slot


@pytest.fixture
def booking_date() -> date:
    return date(2026, 8, 15)


@pytest.fixture
async def booking(
    db_session: AsyncSession,
    regular_user: User,
    room: Room,
    time_slot: TimeSlot,
    booking_date: date,
) -> Booking:
    db_booking = Booking(
        room_id=room.id,
        user_id=regular_user.id,
        date=booking_date,
        time_slot_id=time_slot.id,
    )
    db_session.add(db_booking)
    await db_session.commit()
    await db_session.refresh(db_booking)
    return db_booking
