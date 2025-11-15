# app/services/subject_service.py
from bson import ObjectId
from app.db import db
from app.models.subject import SubjectCreate, SubjectBase

subjects_col = db["subjects"]


# Helper function to convert Mongo document
def subject_to_dict(subject):
    if not subject:
        return None

    subject["_id"] = str(subject["_id"])
    return subject


# -----------------------------
# CREATE SUBJECT
# -----------------------------
async def create_subject(data: SubjectCreate):
    # Check duplicate subject code
    existing = await subjects_col.find_one({"code": data.code})
    if existing:
        return None

    doc = data.dict()
    result = await subjects_col.insert_one(doc)

    created = await subjects_col.find_one({"_id": result.inserted_id})
    return subject_to_dict(created)


# -----------------------------
# GET ALL SUBJECTS
# -----------------------------
async def get_all_subjects():
    subjects = await subjects_col.find().to_list(None)
    return [subject_to_dict(s) for s in subjects]


# -----------------------------
# GET SUBJECT BY ID
# -----------------------------
async def get_subject_by_id(subject_id: str):
    if not ObjectId.is_valid(subject_id):
        return None

    subject = await subjects_col.find_one({"_id": ObjectId(subject_id)})
    return subject_to_dict(subject)


# -----------------------------
# UPDATE SUBJECT
# -----------------------------
async def update_subject_details(subject_id: str, data: SubjectBase):
    if not ObjectId.is_valid(subject_id):
        return None

    update_data = {"$set": data.dict()}

    result = await subjects_col.update_one(
        {"_id": ObjectId(subject_id)}, update_data
    )

    if result.matched_count == 0:
        return None

    updated = await subjects_col.find_one({"_id": ObjectId(subject_id)})
    return subject_to_dict(updated)


# -----------------------------
# DELETE SUBJECT
# -----------------------------
async def remove_subject(subject_id: str):
    if not ObjectId.is_valid(subject_id):
        return False

    result = await subjects_col.delete_one({"_id": ObjectId(subject_id)})
    return result.deleted_count > 0
