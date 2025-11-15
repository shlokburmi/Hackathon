from pydantic import BaseModel
from typing import List, Optional

class SubjectBase(BaseModel):
    name: str
    code: str
    department: Optional[str] = None
    weekly_sessions: int = 3
    duration_minutes: int = 60
    faculty_ids: List[str] = []  # Faculties who can teach this

class SubjectCreate(SubjectBase):
    pass

class SubjectOut(SubjectBase):
    id: str

code: str  # ex: CS101
