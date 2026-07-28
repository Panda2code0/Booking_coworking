"""Room CRUD endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_rooms_list(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.get("/rooms/", headers=user_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == room.name
    assert data[0]["capacity"] == room.capacity


@pytest.mark.asyncio
async def test_get_room_by_id(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.get(f"/rooms/{room.id}", headers=user_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == room.id
    assert data["name"] == room.name


@pytest.mark.asyncio
async def test_get_room_not_found(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    response = await client.get("/rooms/9999", headers=user_auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Комната не найдена."


@pytest.mark.asyncio
async def test_create_room_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/rooms/",
        json={"name": "New Room", "capacity": 8},
        headers=admin_auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Room"
    assert data["capacity"] == 8


@pytest.mark.asyncio
async def test_update_room_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.patch(
        f"/rooms/{room.id}",
        json={"name": "Updated Room", "capacity": 12},
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Room"
    assert data["capacity"] == 12


@pytest.mark.asyncio
async def test_delete_room_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.delete(
        f"/rooms/{room.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204

    get_response = await client.get(
        f"/rooms/{room.id}",
        headers=admin_auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_room_forbidden_for_user(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/rooms/",
        json={"name": "Forbidden Room", "capacity": 4},
        headers=user_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Недостаточно прав для выполнения операции."


@pytest.mark.asyncio
async def test_update_room_forbidden_for_user(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.patch(
        f"/rooms/{room.id}",
        json={"name": "User Update"},
        headers=user_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_room_forbidden_for_user(
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
async def test_create_room_duplicate_name(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.post(
        "/rooms/",
        json={"name": room.name, "capacity": 3},
        headers=admin_auth_headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Комната с таким названием уже существует."


@pytest.mark.asyncio
async def test_update_room_duplicate_name(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    room,
    another_room,
) -> None:
    response = await client.patch(
        f"/rooms/{another_room.id}",
        json={"name": room.name},
        headers=admin_auth_headers,
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_room_not_found(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
) -> None:
    response = await client.patch(
        "/rooms/9999",
        json={"name": "Missing"},
        headers=admin_auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_rooms_availability_all_free(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    room,
    time_slot,
    booking_date,
) -> None:
    response = await client.get(
        "/rooms/availability",
        params={"date": booking_date.isoformat()},
        headers=user_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["room_id"] == room.id
    assert data[0]["room_name"] == room.name
    assert data[0]["date"] == booking_date.isoformat()
    assert len(data[0]["slots"]) == 1
    assert data[0]["slots"][0]["slot_id"] == time_slot.id
    assert data[0]["slots"][0]["is_available"] is True


@pytest.mark.asyncio
async def test_get_rooms_availability_with_booking(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    room,
    time_slot,
    booking,
    booking_date,
) -> None:
    response = await client.get(
        "/rooms/availability",
        params={"date": booking_date.isoformat()},
        headers=user_auth_headers,
    )

    assert response.status_code == 200
    slot = response.json()[0]["slots"][0]
    assert slot["slot_id"] == time_slot.id
    assert slot["is_available"] is False


@pytest.mark.asyncio
async def test_get_rooms_availability_multiple_rooms(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    room,
    another_room,
    time_slot,
    booking_date,
) -> None:
    response = await client.get(
        "/rooms/availability",
        params={"date": booking_date.isoformat()},
        headers=user_auth_headers,
    )

    assert response.status_code == 200
    room_ids = {item["room_id"] for item in response.json()}
    assert room_ids == {room.id, another_room.id}


@pytest.mark.asyncio
async def test_get_rooms_availability_requires_auth(
    client: AsyncClient,
    booking_date,
) -> None:
    response = await client.get(
        "/rooms/availability",
        params={"date": booking_date.isoformat()},
    )

    assert response.status_code == 401
