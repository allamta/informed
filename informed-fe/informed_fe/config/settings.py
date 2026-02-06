import os

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEBUG: bool = False
    LOG_LEVEL: str
    INFORMED_BE_URL: str
    APP_ENV: str
    MAX_UPLOAD_SIZE_MB: int

    class Config:
        env_file = f"src/config/{os.getenv('APP_ENV', 'dev')}.env"
        env_file_encoding = "utf-8"

settings = Settings()
