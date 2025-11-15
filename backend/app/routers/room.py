# app/routers/room.py

from fastapi import APIRouter, HTTPException
from app.models.room import RoomCreate, RoomOut
from app.services.room_service import (
    add_room_service,
    get_all_rooms_service,
    get_room_service,
    update_room_service,
    delete_room_service
)

router = APIRouter(prefix="/room", tags=["Room"])

@router.post("/add")
async def add_room(data: RoomCreate):
    room_id = await add_room_service(data)
    return {"status": "success", "room_id": room_id}

@router.get("/all")
async def get_all_rooms():
    rooms = await get_all_rooms_service()
    return rooms

@router.get("/{room_id}")
async def get_room(room_id: str):
    room = await get_room_service(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/update/{room_id}")
async def update_room(room_id: str, data: RoomCreate):
    await update_room_service(room_id, data)
    return {"status": "updated"}

@router.delete("/delete/{room_id}")
async def delete_room(room_id: str):
    await delete_room_service(room_id)
    return {"status": "deleted"}
