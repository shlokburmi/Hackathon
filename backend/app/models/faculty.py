from pydantic import BaseModel
from typing import Optional, List

class FacultyBase(BaseModel):
    name: str
    email: str
    department: str
    max_weekly_load: int
    subjects_can_teach: List[str] = []
    available_slots: List[int] = []
    password: str

class FacultyCreate(FacultyBase):
    password: str   # optional, if you want auth

class FacultyOut(FacultyBase):
    id: str
    
    # FIX: Changed 'orm_mode' to 'from_attributes'
    class Config:
        from_attributes = True