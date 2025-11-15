# app/routers/faculty.py
from fastapi import APIRouter, Depends, HTTPException
from app.models.faculty import FacultyCreate, FacultyOut, FacultyBase
# Import all your functions from the new service file
from app.services import faculty_service

router = APIRouter(prefix="/faculty", tags=["Faculty"])

# ---- ADD FACULTY ----
# Now, this endpoint is clean and only handles the API logic.
@router.post("/add", response_model=FacultyOut)
async def add_faculty(data: FacultyCreate):
    
    # Call the service function to do the database work
    new_faculty = await faculty_service.create_faculty(data)
    
    if not new_faculty:
        raise HTTPException(status_code=400, detail="Email already exists")

    return new_faculty


# ---- GET ALL FACULTY ----
@router.get("/all", response_model=list[FacultyOut])
async def get_all_faculty():
    return await faculty_service.get_all_faculties()


# ---- GET ONE FACULTY ----
@router.get("/{faculty_id}", response_model=FacultyOut)
async def get_faculty(faculty_id: str):
    fac = await faculty_service.get_faculty_by_id(faculty_id)
    if not fac:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return fac


# ---- UPDATE FACULTY ----
@router.put("/update/{faculty_id}", response_model=FacultyOut)
async def update_faculty(faculty_id: str, data: FacultyBase):
    updated = await faculty_service.update_faculty_details(faculty_id, data)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return updated


# ---- DELETE FACULTY ----
@router.delete("/delete/{faculty_id}")
async def delete_faculty(faculty_id: str):
    success = await faculty_service.remove_faculty(faculty_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return {"message": "Faculty deleted successfully"}


# ---- ADD/UPDATE FACULTY AVAILABILITY ----
@router.put("/availability/{faculty_id}")
async def update_availability(faculty_id: str, availability: dict):
    success = await faculty_service.set_faculty_availability(faculty_id, availability)

    if not success:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return {"message": "Availability updated"}