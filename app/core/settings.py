"""
Core Settings - Centralized configuration
"""
import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App Info
    app_name: str = "Food Advisor Agent"
    app_version: str = "3.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Database URLs
    postgres_url: str = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/foodadvisor")
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME", "foodadvisor")
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # CORS Settings
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "https://foodadvisor.yourdomain.com"
    ]
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()