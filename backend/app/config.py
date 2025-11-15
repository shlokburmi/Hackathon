# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Accept either MONGO_URI or MONGO_URL env key (your .env uses MONGO_URL)
    MONGO_URI: str = os.getenv("MONGO_URI") or os.getenv("MONGO_URL")
    DB_NAME: str = os.getenv("DB_NAME", "timetable")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

settings = Settings()
