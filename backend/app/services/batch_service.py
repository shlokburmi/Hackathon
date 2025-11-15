from app.db import db
from bson import ObjectId

batch_col = db["batches"]

# Convert Mongo document to dict
def serialize(batch):
    batch["id"] = str(batch["_id"])
    batch.pop("_id")
    return batch

# CREATE
async def create_batch(data):
    result = await batch_col.insert_one(data.dict())
    new_batch = await batch_col.find_one({"_id": result.inserted_id})
    return serialize(new_batch)

# GET ALL
async def get_batches():
    batches = []
    async for batch in batch_col.find():
        batches.append(serialize(batch))
    return batches

# GET ONE
async def get_batch(batch_id: str):
    batch = await batch_col.find_one({"_id": ObjectId(batch_id)})
    return serialize(batch) if batch else None

# UPDATE
async def update_batch(batch_id: str, data):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await batch_col.update_one({"_id": ObjectId(batch_id)}, {"$set": update_data})
    updated = await batch_col.find_one({"_id": ObjectId(batch_id)})
    return serialize(updated)

# DELETE
async def delete_batch(batch_id: str):
    await batch_col.delete_one({"_id": ObjectId(batch_id)})
    return True
