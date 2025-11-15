# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

if not settings.MONGO_URI:
    raise RuntimeError("MONGO_URI (or MONGO_URL) not set in environment")

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]
