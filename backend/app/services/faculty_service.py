# app/services/faculty_service.py
from app.db import db
from app.models.faculty import FacultyCreate, FacultyOut, FacultyBase
from bson import ObjectId
from passlib.context import CryptContext

# bcrypt-safe hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------
# PASSWORD HELPERS
# ---------------------
def get_password_hash(password: str):
    # cast to string + fix >72 bytes bcrypt bug
    password = str(password)[:72]
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(str(plain_password), hashed_password)


# database collection
faculty_col = db["faculties"]


# ---------------------
# SERIALIZER
# ---------------------
def _serialize_faculty(doc: dict) -> FacultyOut:
    """
    Converts MongoDB faculty doc into FacultyOut schema safely.
    Removes password and converts _id to string.
    """
    if not doc:
        return None

    # copy so we don't mutate caller's dict
    s = dict(doc)

    # remove password before returning to client
    s.pop("password", None)

    return FacultyOut(
        id=str(s.get("_id")),
        name=s.get("name"),
        email=s.get("email"),
        department=s.get("department"),
        max_weekly_load=s.get("max_weekly_load"),
        subjects_can_teach=s.get("subjects_can_teach", []),
        available_slots=s.get("available_slots", [])
    )


# ---------------------
# CREATE
# ---------------------
async def create_faculty(data: FacultyCreate):
    # check duplicate email
    existing = await faculty_col.find_one({"email": data.email})
    if existing:
        return None

    doc = data.dict()
    # hash password safely
    doc["password"] = get_password_hash(data.password)

    # use a real ObjectId
    doc["_id"] = ObjectId()

    await faculty_col.insert_one(doc)

    # fetch the created document so fields are normalized
    created = await faculty_col.find_one({"_id": doc["_id"]})
    return _serialize_faculty(created)


# ---------------------
# READ ALL
# ---------------------
async def get_all_faculties():
    results = []
    cursor = faculty_col.find({})
    async for fac in cursor:
        results.append(_serialize_faculty(fac))
    return results


# ---------------------
# READ BY ID
# ---------------------
async def get_faculty_by_id(faculty_id: str):
    if not ObjectId.is_valid(faculty_id):
        return None

    fac = await faculty_col.find_one({"_id": ObjectId(faculty_id)})
    if not fac:
        return None
    return _serialize_faculty(fac)


# ---------------------
# READ BY EMAIL (needed for login)
# ---------------------
async def get_faculty_by_email(email: str):
    # return the raw document (contains password) for authentication checks
    return await faculty_col.find_one({"email": email})


# ---------------------
# UPDATE
# ---------------------
async def update_faculty_details(faculty_id: str, data: FacultyBase):
    if not ObjectId.is_valid(faculty_id):
        return None

    updates = data.dict(exclude_unset=True)

    if "password" in updates:
        updates["password"] = get_password_hash(updates["password"])

    updated = await faculty_col.find_one_and_update(
        {"_id": ObjectId(faculty_id)},
        {"$set": updates},
        return_document=True
    )

    if not updated:
        return None

    return _serialize_faculty(updated)


# ---------------------
# DELETE
# ---------------------
async def remove_faculty(faculty_id: str):
    if not ObjectId.is_valid(faculty_id):
        return False

    result = await faculty_col.delete_one({"_id": ObjectId(faculty_id)})
    return result.deleted_count > 0


# ---------------------
# UPDATE AVAILABILITY
# ---------------------
async def set_faculty_availability(faculty_id: str, availability: dict):
    if not ObjectId.is_valid(faculty_id):
        return False

    result = await faculty_col.update_one(
        {"_id": ObjectId(faculty_id)},
        {"$set": {"availability": availability}}
    )
    return result.modified_count > 0
