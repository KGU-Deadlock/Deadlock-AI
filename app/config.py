import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    
    # application settings
    APP_NAME: str = "Deadlock AI - STT Service"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # OpenAI API settings (Required)
    OPENAI_API_KEY: str  # 필수 값 - .env 파일에 설정 필요
    WHISPER_MODEL: str = "whisper-1"  # OpenAI API uses "whisper-1" model
    
    # file upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 25 * 1024 * 1024  # 25MB
    ALLOWED_EXTENSIONS: set = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}
    
    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
