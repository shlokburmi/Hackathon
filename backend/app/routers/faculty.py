# app/routers/faculty.py

from fastapi import APIRouter, Depends, HTTPException
from app.models.faculty import FacultyCreate, FacultyOut, FacultyBase
from app.services import faculty_service
from app.security import get_current_user

router = APIRouter(prefix="/faculty", tags=["Faculty"])


# -------------------------
# CREATE FACULTY (PUBLIC)
# -------------------------
@router.post("/add", response_model=FacultyOut)
async def add_faculty(data: FacultyCreate):
    new_fac = await faculty_service.create_faculty(data)
    
    if not new_fac:
        raise HTTPException(status_code=400, detail="Email already exists")

    return new_fac


# -------------------------
# GET ALL FACULTY (PROTECTED)
# -------------------------
@router.get("/all", response_model=list[FacultyOut])
async def get_all_faculty(current_user: dict = Depends(get_current_user)):
    return await faculty_service.get_all_faculties()


# -------------------------
# GET ONE FACULTY (PROTECTED)
# -------------------------
@router.get("/{faculty_id}", response_model=FacultyOut)
async def get_faculty(faculty_id: str, current_user: dict = Depends(get_current_user)):
    fac = await faculty_service.get_faculty_by_id(faculty_id)
    if not fac:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return fac


# -------------------------
# UPDATE FACULTY (PROTECTED)
# -------------------------
@router.put("/update/{faculty_id}", response_model=FacultyOut)
async def update_faculty(faculty_id: str, data: FacultyBase, current_user: dict = Depends(get_current_user)):
    updated = await faculty_service.update_faculty_details(faculty_id, data)

    if not updated:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return updated


# -------------------------
# DELETE FACULTY (PROTECTED)
# -------------------------
@router.delete("/delete/{faculty_id}")
async def delete_faculty(faculty_id: str, current_user: dict = Depends(get_current_user)):
    success = await faculty_service.remove_faculty(faculty_id)

    if not success:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return {"message": "Faculty deleted successfully"}


# -------------------------
# UPDATE AVAILABILITY (PROTECTED)
# -------------------------
@router.put("/availability/{faculty_id}")
async def update_availability(faculty_id: str, availability: dict, current_user: dict = Depends(get_current_user)):
    success = await faculty_service.set_faculty_availability(faculty_id, availability)

    if not success:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return {"message": "Availability updated"}
