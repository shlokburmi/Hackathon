# app/routers/subject.py
from fastapi import APIRouter, HTTPException, Depends
from app.models.subject import SubjectCreate, SubjectOut, SubjectBase
# Import the new service
from app.services import subject_service
# Import the dependency from the correct security file
from app.security import get_current_user

router = APIRouter(prefix="/subject", tags=["Subjects"])


# ---- ADD SUBJECT ----
@router.post("/add", response_model=SubjectOut)
async def add_subject(data: SubjectCreate, current_user: dict = Depends(get_current_user)):
    
    new_subject = await subject_service.create_subject(data)
    
    if not new_subject:
        raise HTTPException(status_code=400, detail="Subject code already exists")

    return new_subject


# ---- GET ALL SUBJECTS ----
# FIX: response_model is now list[SubjectOut]
@router.get("/all", response_model=list[SubjectOut])
async def get_all_subjects(current_user: dict = Depends(get_current_user)):
    return await subject_service.get_all_subjects()


# ---- GET SUBJECT BY ID ----
@router.get("/{subject_id}", response_model=SubjectOut)
async def get_subject(subject_id: str, current_user: dict = Depends(get_current_user)):
    sub = await subject_service.get_subject_by_id(subject_id)

    if not sub:
        # FIX: Changed 4404 to 404
        raise HTTPException(status_code=404, detail="Subject not found")

    return sub


# ---- UPDATE SUBJECT ----
@router.put("/update/{subject_id}", response_model=SubjectOut)
async def update_subject(subject_id: str, data: SubjectBase, current_user: dict = Depends(get_current_user)):
    
    updated = await subject_service.update_subject_details(subject_id, data)

    if not updated:
        raise HTTPException(status_code=404, detail="Subject not found")

    return updated


# ---- DELETE SUBJECT ----
@router.delete("/delete/{subject_id}")
async def delete_subject(subject_id: str, current_user: dict = Depends(get_current_user)):
    
    success = await subject_service.remove_subject(subject_id)

    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")

    return {"message": "Subject deleted successfully"}