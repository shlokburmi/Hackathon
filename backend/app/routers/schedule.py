from fastapi import APIRouter
from app.db import db
from app.services.scheduler import generate_schedule

router = APIRouter(prefix="/schedule", tags=["Scheduling Engine"])


@router.post("/generate")
async def generate_timetable():

    # Fetch data from MongoDB
    subjects = await db["subjects"].find().to_list(None)
    faculties = await db["faculties"].find().to_list(None)
    rooms = await db["rooms"].find().to_list(None)
    batches = await db["batches"].find().to_list(None)

    schedule = await generate_schedule(subjects, faculties, rooms, batches)

    if schedule is None:
        return {"status": "fail", "message": "No valid schedule found"}

    return {"status": "success", "schedule": schedule}



