from fastapi import APIRouter, HTTPException
from app.db import db
from app.models.subject import SubjectCreate, SubjectOut, SubjectBase
from bson import ObjectId

router = APIRouter(prefix="/subject", tags=["Subjects"])


# ---- ADD SUBJECT ----
@router.post("/add", response_model=SubjectOut)
async def add_subject(data: SubjectCreate):
    subject_col = db["subjects"]

    # Check duplicate subject code
    exists = await subject_col.find_one({"code": data.code})
    if exists:
        raise HTTPException(status_code=400, detail="Subject code already exists")

    new_doc = data.dict()
    new_doc["_id"] = str(ObjectId())

    await subject_col.insert_one(new_doc)

    return {"id": new_doc["_id"], **new_doc}


# ---- GET ALL SUBJECTS ----
@router.get("/all", response_model=list[SubjectOut])
async def get_all_subjects():
    subject_col = db["subjects"]
    docs = []
    async for sub in subject_col.find({}):
        docs.append(SubjectOut(id=sub["_id"], **sub))
    return docs


# ---- GET SUBJECT BY ID ----
@router.get("/{subject_id}", response_model=SubjectOut)
async def get_subject(subject_id: str):
    subject_col = db["subjects"]
    sub = await subject_col.find_one({"_id": subject_id})

    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found")

    return SubjectOut(id=sub["_id"], **sub)


# ---- UPDATE SUBJECT ----
@router.put("/update/{subject_id}", response_model=SubjectOut)
async def update_subject(subject_id: str, data: SubjectBase):
    subject_col = db["subjects"]

    updated = await subject_col.find_one_and_update(
        {"_id": subject_id},
        {"$set": data.dict()},
        return_document=True
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Subject not found")

    return SubjectOut(id=updated["_id"], **updated)


# ---- DELETE SUBJECT ----
@router.delete("/delete/{subject_id}")
async def delete_subject(subject_id: str):
    subject_col = db["subjects"]

    result = await subject_col.delete_one({"_id": subject_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subject not found")

    return {"message": "Subject deleted successfully"}
