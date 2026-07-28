from datetime import time

from pydantic import BaseModel, ConfigDict


class TimeSlotCreate(BaseModel):
    room_id: int
    start_time: time
    end_time: time


class TimeSlotUpdate(BaseModel):
    room_id: int | None = None
    start_time: time | None = None
    end_time: time | None = None


class TimeSlotResponse(BaseModel):
    id: int
    room_id: int
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)
