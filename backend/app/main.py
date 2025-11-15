from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import the new auth router
from app.routers import faculty, subject, schedule, room, batch, auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the new auth router to your app
app.include_router(auth.router)

# Include all your other routers
app.include_router(faculty.router)
app.include_router(subject.router)
app.include_router(schedule.router)
app.include_router(room.router)
app.include_router(batch.router)