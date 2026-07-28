"""Role-based access control tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_cannot_create_room(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/rooms/",
        json={"name": "User Room", "capacity": 3},
        headers=user_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_delete_room(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.delete(
        f"/rooms/{room.id}",
        headers=user_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_create_slot(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.post(
        "/slots/",
        json={
            "room_id": room.id,
            "start_time": "16:00:00",
            "end_time": "17:00:00",
        },
        headers=user_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_delete_slot(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    time_slot,
) -> None:
    response = await client.delete(
        f"/slots/{time_slot.id}",
        headers=user_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_view_all_bookings(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    booking,
) -> None:
    response = await client.get("/bookings/", headers=user_auth_headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_create_room(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/rooms/",
        json={"name": "Admin Room", "capacity": 6},
        headers=admin_auth_headers,
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_admin_can_delete_room(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.delete(
        f"/rooms/{room.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_admin_can_create_slot(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.post(
        "/slots/",
        json={
            "room_id": room.id,
            "start_time": "08:00:00",
            "end_time": "09:00:00",
        },
        headers=admin_auth_headers,
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_admin_can_delete_slot(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    time_slot,
) -> None:
    response = await client.delete(
        f"/slots/{time_slot.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_admin_can_view_all_bookings(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    booking,
) -> None:
    response = await client.get("/bookings/", headers=admin_auth_headers)

    assert response.status_code == 200
    assert len(response.json()) >= 1
