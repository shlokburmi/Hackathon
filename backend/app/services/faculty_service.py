# app/services/faculty_service.py
from app.db import db
from app.models.faculty import FacultyCreate, FacultyOut, FacultyBase
from bson import ObjectId
from passlib.context import CryptContext

# --- Security Setup ---
# 1. Create a context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Function to hash a password
def get_password_hash(password):
    return pwd_context.hash(password)

# 3. Function to verify a password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
# ------------------------


faculty_col = db["faculties"]

async def create_faculty(data: FacultyCreate):
    """
    Creates a new faculty, hashing the password before storage.
    """
    # Check duplicate
    existing = await faculty_col.find_one({"email": data.email})
    if existing:
        return None  # Return None to indicate failure (duplicate)

    new_doc = data.dict()
    
    # --- Hash the password ---
    # Never store plain-text passwords!
    new_doc["password"] = get_password_hash(data.password)
    # -------------------------

    new_doc["_id"] = str(ObjectId())
    
    await faculty_col.insert_one(new_doc)
    
    # Return the new document as a FacultyOut model
    new_doc["id"] = new_doc["_id"]
    return FacultyOut(**new_doc)


async def get_all_faculties():
    """
    Retrieves all faculties from the database.
    """
    docs = []
    async for fac in faculty_col.find({}):
        fac["id"] = fac["_id"]
        docs.append(FacultyOut(**fac))
    return docs


async def get_faculty_by_id(faculty_id: str):
    """
    Retrieves a single faculty by their ID.
    """
    fac = await faculty_col.find_one({"_id": faculty_id})
    if not fac:
        return None
    
    fac["id"] = fac["_id"]
    return FacultyOut(**fac)


async def get_faculty_by_email(email: str):
    """
    Retrieves a single faculty by their email (needed for login).
    """
    fac = await faculty_col.find_one({"email": email})
    return fac


async def update_faculty_details(faculty_id: str, data: FacultyBase):
    """
    Updates a faculty's details.
    Note: This doesn't update the password, only base details.
    """
    update_data = data.dict(exclude_unset=True) # Exclude unset to avoid overwriting

    # If password is in the update data, make sure to hash it
    # (Though typically password updates are handled separately)
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])

    updated = await faculty_col.find_one_and_update(
        {"_id": faculty_id},
        {"$set": update_data},
        return_document=True
    )

    if not updated:
        return None

    updated["id"] = updated["_id"]
    return FacultyOut(**updated)


async def remove_faculty(faculty_id: str):
    """
    Deletes a faculty from the database.
    """
    result = await faculty_col.delete_one({"_id": faculty_id})
    return result.deleted_count > 0


async def set_faculty_availability(faculty_id: str, availability: dict):
    """
    Updates a faculty's availability.
    """
    updated = await faculty_col.update_one(
        {"_id": faculty_id},
        {"$set": {"availability": availability}}
    )
    return updated.modified_count > 0