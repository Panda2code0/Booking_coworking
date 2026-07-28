"""Time slot CRUD endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_slots_list(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    time_slot,
) -> None:
    response = await client.get("/slots/", headers=user_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == time_slot.id
    assert data[0]["room_id"] == time_slot.room_id


@pytest.mark.asyncio
async def test_get_slot_by_id(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    time_slot,
) -> None:
    response = await client.get(
        f"/slots/{time_slot.id}",
        headers=user_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == time_slot.id
    assert data["start_time"] == "09:00:00"
    assert data["end_time"] == "10:00:00"


@pytest.mark.asyncio
async def test_get_slot_not_found(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    response = await client.get("/slots/9999", headers=user_auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Слот не найден."


@pytest.mark.asyncio
async def test_create_slot_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.post(
        "/slots/",
        json={
            "room_id": room.id,
            "start_time": "11:00:00",
            "end_time": "12:00:00",
        },
        headers=admin_auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["room_id"] == room.id
    assert data["start_time"] == "11:00:00"


@pytest.mark.asyncio
async def test_create_slot_nonexistent_room(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/slots/",
        json={
            "room_id": 9999,
            "start_time": "11:00:00",
            "end_time": "12:00:00",
        },
        headers=admin_auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Комната не существует."


@pytest.mark.asyncio
async def test_update_slot_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    time_slot,
) -> None:
    response = await client.patch(
        f"/slots/{time_slot.id}",
        json={"start_time": "10:00:00", "end_time": "11:00:00"},
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["start_time"] == "10:00:00"
    assert data["end_time"] == "11:00:00"


@pytest.mark.asyncio
async def test_delete_slot_admin(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    time_slot,
) -> None:
    response = await client.delete(
        f"/slots/{time_slot.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204

    get_response = await client.get(
        f"/slots/{time_slot.id}",
        headers=admin_auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_slot_forbidden_for_user(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    room,
) -> None:
    response = await client.post(
        "/slots/",
        json={
            "room_id": room.id,
            "start_time": "14:00:00",
            "end_time": "15:00:00",
        },
        headers=user_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_slot_forbidden_for_user(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    time_slot,
) -> None:
    response = await client.patch(
        f"/slots/{time_slot.id}",
        json={"start_time": "15:00:00"},
        headers=user_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_slot_forbidden_for_user(
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
async def test_update_slot_not_found(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
) -> None:
    response = await client.patch(
        "/slots/9999",
        json={"start_time": "12:00:00"},
        headers=admin_auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_slot_invalid_room(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    time_slot,
) -> None:
    response = await client.patch(
        f"/slots/{time_slot.id}",
        json={"room_id": 9999},
        headers=admin_auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Ошибка обновления слота."
