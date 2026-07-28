"""Authentication endpoint tests."""

import pytest
from httpx import AsyncClient
from jose import jwt

from app.core.config import settings


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={"username": "new_user", "password": "secure_pass"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_user"
    assert data["role"] == "employee"
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient, regular_user) -> None:
    response = await client.post(
        "/auth/register",
        json={"username": "employee", "password": "another_pass"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Пользователь с таким именем уже существует."


@pytest.mark.asyncio
async def test_login_success(
    client: AsyncClient,
    regular_user,
    user_credentials: dict[str, str],
) -> None:
    response = await client.post(
        "/auth/login",
        data={
            "username": user_credentials["username"],
            "password": user_credentials["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient,
    regular_user,
    user_credentials: dict[str, str],
) -> None:
    response = await client.post(
        "/auth/login",
        data={
            "username": user_credentials["username"],
            "password": "wrong_password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Неверное имя пользователя или пароль."


@pytest.mark.asyncio
async def test_login_wrong_user(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        data={"username": "unknown_user", "password": "any_password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Неверное имя пользователя или пароль."


@pytest.mark.asyncio
async def test_login_returns_jwt(
    client: AsyncClient,
    regular_user,
    user_credentials: dict[str, str],
) -> None:
    response = await client.post(
        "/auth/login",
        data={
            "username": user_credentials["username"],
            "password": user_credentials["password"],
        },
    )

    assert response.status_code == 200
    token = response.json()["access_token"]
    assert isinstance(token, str)
    assert len(token.split(".")) == 3


@pytest.mark.asyncio
async def test_protected_endpoint_with_token(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    response = await client.get("/rooms/", headers=user_auth_headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient) -> None:
    response = await client.get("/rooms/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_invalid_token(
    client: AsyncClient,
    auth_headers,
) -> None:
    response = await client.get(
        "/rooms/",
        headers=auth_headers("invalid.jwt.token"),
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "API работает"}


@pytest.mark.asyncio
async def test_token_for_deleted_user(
    client: AsyncClient,
    regular_user,
    user_token: str,
    auth_headers,
    db_session,
) -> None:
    await db_session.delete(regular_user)
    await db_session.commit()

    response = await client.get(
        "/rooms/",
        headers=auth_headers(user_token),
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_without_subject(
    client: AsyncClient,
    auth_headers,
) -> None:
    token = jwt.encode(
        {"exp": 9999999999},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    response = await client.get("/rooms/", headers=auth_headers(token))

    assert response.status_code == 401
