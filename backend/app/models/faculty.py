# app/models/faculty.py

from pydantic import BaseModel, EmailStr
from typing import List

class FacultyBase(BaseModel):
    name: str
    email: EmailStr
    department: str
    max_weekly_load: int
    subjects_can_teach: List[str] = []
    available_slots: List[str] = []

class FacultyCreate(FacultyBase):
    password: str

class FacultyOut(FacultyBase):
    id: str  # returned to frontend (no password!)
