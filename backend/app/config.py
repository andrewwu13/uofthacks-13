from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "uofthacks"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 50
    MONGODB_TIMEOUT_MS: int = 5000
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Backboard
    BACKBOARD_API_KEY: str = ""
    
    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
