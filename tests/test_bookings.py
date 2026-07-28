"""Booking business logic tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_booking(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    room,
    time_slot,
    booking_date,
) -> None:
    response = await client.post(
        "/bookings/",
        json={
            "room_id": room.id,
            "date": booking_date.isoformat(),
            "time_slot_id": time_slot.id,
        },
        headers=user_auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["room_id"] == room.id
    assert data["time_slot_id"] == time_slot.id
    assert data["date"] == booking_date.isoformat()
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_my_bookings(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    booking,
) -> None:
    response = await client.get("/bookings/me", headers=user_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == booking.id


@pytest.mark.asyncio
async def test_delete_own_booking(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    booking,
) -> None:
    response = await client.delete(
        f"/bookings/{booking.id}",
        headers=user_auth_headers,
    )

    assert response.status_code == 204

    list_response = await client.get("/bookings/me", headers=user_auth_headers)
    assert list_response.json() == []


@pytest.mark.asyncio
async def test_delete_other_user_booking_forbidden(
    client: AsyncClient,
    other_user_auth_headers: dict[str, str],
    booking,
) -> None:
    response = await client.delete(
        f"/bookings/{booking.id}",
        headers=other_user_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Недостаточно прав для отмены бронирования."


@pytest.mark.asyncio
async def test_double_booking_conflict(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    other_user_auth_headers: dict[str, str],
    room,
    time_slot,
    booking_date,
) -> None:
    first = await client.post(
        "/bookings/",
        json={
            "room_id": room.id,
            "date": booking_date.isoformat(),
            "time_slot_id": time_slot.id,
        },
        headers=user_auth_headers,
    )
    assert first.status_code == 201

    second = await client.post(
        "/bookings/",
        json={
            "room_id": room.id,
            "date": booking_date.isoformat(),
            "time_slot_id": time_slot.id,
        },
        headers=other_user_auth_headers,
    )

    assert second.status_code == 409
    assert second.json()["detail"] == "Комната уже забронирована на эту дату и время."


@pytest.mark.asyncio
async def test_booking_nonexistent_room(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    time_slot,
    booking_date,
) -> None:
    response = await client.post(
        "/bookings/",
        json={
            "room_id": 9999,
            "date": booking_date.isoformat(),
            "time_slot_id": time_slot.id,
        },
        headers=user_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Комната не найдена."


@pytest.mark.asyncio
async def test_booking_nonexistent_slot(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    room,
    booking_date,
) -> None:
    response = await client.post(
        "/bookings/",
        json={
            "room_id": room.id,
            "date": booking_date.isoformat(),
            "time_slot_id": 9999,
        },
        headers=user_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Слот не найден."


@pytest.mark.asyncio
async def test_booking_slot_not_in_room(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
    another_room,
    time_slot,
    booking_date,
) -> None:
    response = await client.post(
        "/bookings/",
        json={
            "room_id": another_room.id,
            "date": booking_date.isoformat(),
            "time_slot_id": time_slot.id,
        },
        headers=user_auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Слот не принадлежит указанной комнате."


@pytest.mark.asyncio
async def test_admin_get_all_bookings(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    booking,
) -> None:
    response = await client.get("/bookings/", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == booking.id


@pytest.mark.asyncio
async def test_delete_nonexistent_booking(
    client: AsyncClient,
    user_auth_headers: dict[str, str],
) -> None:
    response = await client.delete(
        "/bookings/9999",
        headers=user_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Бронирование не найдено."


@pytest.mark.asyncio
async def test_admin_can_delete_other_user_booking(
    client: AsyncClient,
    admin_auth_headers: dict[str, str],
    booking,
) -> None:
    response = await client.delete(
        f"/bookings/{booking.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204

    list_response = await client.get("/bookings/", headers=admin_auth_headers)
    assert list_response.json() == []
