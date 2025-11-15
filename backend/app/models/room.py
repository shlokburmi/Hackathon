# app/models/room.py
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class RoomBase(BaseModel):
    name: str
    capacity: int
    room_type: str  # e.g., "lecture", "lab", "seminar"

class RoomCreate(RoomBase):
    pass

class RoomOut(RoomBase):
    id: str = Field(default_factory=str)

    class Config:
        from_attributes = True
