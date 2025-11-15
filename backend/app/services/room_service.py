# app/services/room_service.py

from app.db import db

room_col = db["rooms"]

async def add_room_service(data):
    room_dict = data.dict()
    result = await room_col.insert_one(room_dict)
    return str(result.inserted_id)

async def get_all_rooms_service():
    rooms = await room_col.find().to_list(None)
    return rooms

async def get_room_service(room_id):
    from bson import ObjectId
    return await room_col.find_one({"_id": ObjectId(room_id)})

async def update_room_service(room_id, data):
    from bson import ObjectId
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    await room_col.update_one({"_id": ObjectId(room_id)}, {"$set": update_data})
    return True

async def delete_room_service(room_id):
    from bson import ObjectId
    await room_col.delete_one({"_id": ObjectId(room_id)})
    return True
