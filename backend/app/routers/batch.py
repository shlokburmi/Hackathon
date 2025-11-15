from fastapi import APIRouter, HTTPException
from app.models.batch import BatchCreate, BatchUpdate, BatchOut
from app.services.batch_service import (
    create_batch, get_batches, get_batch, update_batch, delete_batch
)

router = APIRouter(prefix="/batch", tags=["Batch"])

# CREATE
@router.post("/add", response_model=BatchOut)
async def add_batch(data: BatchCreate):
    batch = await create_batch(data)
    return batch

# GET ALL
@router.get("/all")
async def list_batches():
    return await get_batches()

# GET ONE
@router.get("/{batch_id}", response_model=BatchOut)
async def get_single_batch(batch_id: str):
    batch = await get_batch(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

# UPDATE
@router.put("/update/{batch_id}", response_model=BatchOut)
async def update_single_batch(batch_id: str, data: BatchUpdate):
    batch = await update_batch(batch_id, data)
    return batch

# DELETE
@router.delete("/delete/{batch_id}")
async def remove_batch(batch_id: str):
    await delete_batch(batch_id)
    return {"message": "Batch deleted successfully"}
