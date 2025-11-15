from fastapi import APIRouter, Depends, HTTPException
from app.db import db
from app.models.faculty import FacultyCreate, FacultyOut, FacultyBase
from bson import ObjectId

router = APIRouter(prefix="/faculty", tags=["Faculty"])


# ---- ADD FACULTY ----
@router.post("/add", response_model=FacultyOut)
async def add_faculty(data: FacultyCreate):
    faculty_col = db["faculties"]

    # check duplicate
    existing = await faculty_col.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_doc = data.dict()
    new_doc["_id"] = str(ObjectId())

    await faculty_col.insert_one(new_doc)

    return {
        "id": new_doc["_id"],
        **new_doc
    }


# ---- GET ALL FACULTY ----
@router.get("/all", response_model=list[FacultyOut])
async def get_all_faculty():
    faculty_col = db["faculties"]
    docs = []
    async for fac in faculty_col.find({}):
        fac["id"] = fac["_id"]
        docs.append(FacultyOut(**fac))
    return docs


# ---- GET ONE FACULTY ----
@router.get("/{faculty_id}", response_model=FacultyOut)
async def get_faculty(faculty_id: str):
    faculty_col = db["faculties"]
    fac = await faculty_col.find_one({"_id": faculty_id})
    if not fac:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    fac["id"] = fac["_id"]
    return FacultyOut(**fac)


# ---- UPDATE FACULTY ----
@router.put("/update/{faculty_id}", response_model=FacultyOut)
async def update_faculty(faculty_id: str, data: FacultyBase):
    faculty_col = db["faculties"]

    updated = await faculty_col.find_one_and_update(
        {"_id": faculty_id},
        {"$set": data.dict()},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Faculty not found")

    updated["id"] = updated["_id"]
    return FacultyOut(**updated)


# ---- DELETE FACULTY ----
@router.delete("/delete/{faculty_id}")
async def delete_faculty(faculty_id: str):
    faculty_col = db["faculties"]
    result = await faculty_col.delete_one({"_id": faculty_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return {"message": "Faculty deleted successfully"}


# ---- ADD/UPDATE FACULTY AVAILABILITY ----
@router.put("/availability/{faculty_id}")
async def update_availability(faculty_id: str, availability: dict):
    """
    availability format example:
    {
        "unavailable": ["Mon 10:00", "Wed 14:00"]
    }
    """
    faculty_col = db["faculties"]

    updated = await faculty_col.update_one(
        {"_id": faculty_id},
        {"$set": {"availability": availability}}
    )

    if updated.modified_count == 0:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return {"message": "Availability updated"}
