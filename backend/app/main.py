from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import faculty, subject, schedule, room, batch

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(faculty.router)
app.include_router(subject.router)
app.include_router(schedule.router)
app.include_router(room.router)
app.include_router(batch.router)




