"""
Application configuration using pydantic-settings
Environment variables are loaded from .env file
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # =========================================
    # Database Configuration
    # =========================================
    
    # Redis (session cache, motor state)
    REDIS_URL: str = "redis://localhost:6379"
    
    # MongoDB (cold storage, preferences, telemetry)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "gen_ui"
    MONGODB_DB: str = "gen_ui"  # Alias for backwards compatibility
    MONGODB_MIN_POOL_SIZE: int = Field(default=1, description="Minimum connections in pool")
    MONGODB_MAX_POOL_SIZE: int = Field(default=10, description="Maximum connections in pool")
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = Field(default=5000, description="Timeout for server selection")
    MONGODB_CONNECT_TIMEOUT_MS: int = Field(default=10000, description="Connection timeout")
    
    # Vector DB (Pinecone or Qdrant)
    VECTOR_DB_URL: str = ""
    VECTOR_DB_API_KEY: str = ""
    
    # =========================================
    # External Services
    # =========================================
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Shopify
    SHOPIFY_API_KEY: str = ""
    SHOPIFY_API_SECRET: str = ""
    SHOPIFY_STORE_URL: str = ""
    
    # Backboard.io
    BACKBOARD_API_KEY: str = ""
    
    # Amplitude
    AMPLITUDE_API_KEY: str = ""
    
    # Kafka/RedPanda
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Ignore extra env vars
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid re-reading .env on every call.
    """
    return Settings()


# Default settings instance
settings = get_settings()
