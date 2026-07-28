from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class BookingCreate(BaseModel):
    room_id: int
    date: date
    time_slot_id: int


class BookingResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    date: date
    time_slot_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
