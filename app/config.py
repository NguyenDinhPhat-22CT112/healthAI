"""
Application Configuration Settings
Database URLs, API keys, and environment-specific settings
"""
import os
from pydantic_settings import BaseSettings
from urllib.parse import urlparse


class Settings(BaseSettings):
    # App Info
    app_name: str = os.getenv("APP_NAME", "Food Advisor Agent")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Database URLs
    postgres_url: str = os.getenv("POSTGRES_URL", "postgresql://username:password@localhost:5432/database_name")
    
    # MongoDB - Hỗ trợ cả MongoDB Atlas và local MongoDB
    # MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/dbname?retryWrites=true&w=majority
    # Local MongoDB: mongodb://localhost:27017/
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME", "HealthAI")
    
    # API keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    
    # CORS Settings
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
    
    def get_mongo_db_name(self) -> str:
        """
        Lấy database name từ MongoDB connection string hoặc từ env variable
        MongoDB Atlas connection string có thể chứa database name trong path
        """
        if not self.mongo_url or self.mongo_url == "mongodb://localhost:27017/":
            return self.mongo_db_name
        
        try:
            # Parse MongoDB connection string
            if "mongodb+srv://" in self.mongo_url:
                # MongoDB Atlas format: mongodb+srv://user:pass@cluster.net/dbname?options
                parts = self.mongo_url.split("/")
                if len(parts) > 3:
                    db_part = parts[3].split("?")[0]  # Lấy phần database name trước dấu ?
                    if db_part:
                        return db_part
            else:
                # Standard MongoDB format: mongodb://host:port/dbname?options
                parsed = urlparse(self.mongo_url)
                if parsed.path and parsed.path != "/":
                    db_name = parsed.path.lstrip("/").split("?")[0]
                    if db_name:
                        return db_name
        except Exception:
            pass
        
        return self.mongo_db_name


settings = Settings()

