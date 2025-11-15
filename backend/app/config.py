from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    SECRET_KEY: str
    GROQ_API_KEY: str  # <-- ADD THIS

    class Config:
        env_file = ".env"
        extra = "allow"   # optional, allows future extra vars

settings = Settings()