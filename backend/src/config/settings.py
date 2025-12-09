"""
Configuration settings for the ETL service.
"""
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "ETL Service"
    debug: bool = False
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/etl_db",
        env="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # Celery
    celery_broker_url: str = Field(
        default="amqp://admin:password@localhost:5672//",
        env="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1",
        env="CELERY_RESULT_BACKEND"
    )
    
    # MongoDB (source database)
    mongodb_url: str = Field(
        default="mongodb://root:password@localhost:27017/",
        env="MONGODB_URL"
    )
    
    # Security
    secret_key: str = Field(
        default="your-super-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()