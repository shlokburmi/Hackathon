# app/services/faculty_service.py
from app.db import db
from app.models.faculty import FacultyCreate, FacultyOut, FacultyBase
from bson import ObjectId
from passlib.context import CryptContext

# bcrypt-safe hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    # bcrypt limitation: max 72 bytes -> truncate safely
    return pwd_context.hash(str(password)[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(str(plain_password), hashed_password)

faculty_col = db["faculties"]

def _serialize_faculty(doc: dict) -> FacultyOut:
    # remove password if present (prevent Pydantic from seeing it)
    doc = dict(doc)  # shallow copy to avoid mutating original
    doc.pop("password", None)
    return FacultyOut(
        id=str(doc.get("_id") or doc.get("id")),
        name=doc["name"],
        email=doc["email"],
        department=doc["department"],
        max_weekly_load=doc["max_weekly_load"],
        subjects_can_teach=doc.get("subjects_can_teach", []),
        available_slots=doc.get("available_slots", []),
    )

async def create_faculty(data: FacultyCreate):
    existing = await faculty_col.find_one({"email": data.email})
    if existing:
        return None
    doc = data.dict()
    doc["password"] = get_password_hash(data.password)
    doc["_id"] = str(ObjectId())
    await faculty_col.insert_one(doc)
    return _serialize_faculty(doc)

async def get_all_faculties():
    out = []
    async for f in faculty_col.find({}):
        out.append(_serialize_faculty(f))
    return out

async def get_faculty_by_id(faculty_id: str):
    fac = await faculty_col.find_one({"_id": faculty_id})
    if not fac:
        return None
    return _serialize_faculty(fac)

async def get_faculty_by_email(email: str):
    return await faculty_col.find_one({"email": email})

async def update_faculty_details(faculty_id: str, data: FacultyBase):
    updates = data.dict(exclude_unset=True)
    if "password" in updates:
        updates["password"] = get_password_hash(updates["password"])
    updated = await faculty_col.find_one_and_update(
        {"_id": faculty_id},
        {"$set": updates},
        return_document=True
    )
    if not updated:
        return None
    return _serialize_faculty(updated)

async def remove_faculty(faculty_id: str):
    res = await faculty_col.delete_one({"_id": faculty_id})
    return res.deleted_count > 0

async def set_faculty_availability(faculty_id: str, availability: dict):
    res = await faculty_col.update_one({"_id": faculty_id}, {"$set": {"availability": availability}})
    return res.modified_count > 0
