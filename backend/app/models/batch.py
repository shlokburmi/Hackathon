from pydantic import BaseModel, Field
from typing import List

class BatchBase(BaseModel):
    name: str = Field(..., example="CSE-A")
    department: str = Field(..., example="CSE")
    semester: int = Field(..., example=3)
    subjects: List[str] = Field(default_factory=list, example=["CS101", "CS102"])

class BatchCreate(BatchBase):
    pass

class BatchUpdate(BaseModel):
    name: str | None = None
    department: str | None = None
    semester: int | None = None
    subjects: List[str] | None = None

class BatchOut(BatchBase):
    id: str
   
