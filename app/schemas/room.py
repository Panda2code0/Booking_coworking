from datetime import date, time

from pydantic import BaseModel, ConfigDict


class RoomCreate(BaseModel):
    name: str
    capacity: int


class RoomResponse(BaseModel):
    id: int
    name: str
    capacity: int

    model_config = ConfigDict(from_attributes=True)


class RoomUpdate(BaseModel):
    name: str | None = None
    capacity: int | None = None


class SlotAvailability(BaseModel):
    slot_id: int
    start_time: time
    end_time: time
    is_available: bool


class RoomAvailability(BaseModel):
    room_id: int
    room_name: str
    capacity: int
    date: date
    slots: list[SlotAvailability]
