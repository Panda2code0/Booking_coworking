from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.bookings import router as bookings_router
from app.api.rooms import router as rooms_router
from app.api.time_slots import router as slot_router

app = FastAPI(
    title="Meeting Booking API",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(rooms_router)
app.include_router(slot_router)
app.include_router(bookings_router)


@app.get("/")
async def root():
    return {"message": "API работает"}
