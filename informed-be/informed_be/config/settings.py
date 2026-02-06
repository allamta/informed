from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DEBUG: bool = False
    LOG_LEVEL: str
    GROQ_API_KEY: str
    MODEL: str
    PORT: int
    OCR_LANGUAGE: str
    OCR_CONFIDENCE_THRESHOLD: float
    DATABASE_URL: str

    class Config:
        env_file = f"src/config/{os.getenv('APP_ENV', 'dev')}.env"
        env_file_encoding = "utf-8"

settings = Settings()
