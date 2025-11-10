"""
Settings (DB URLs, API keys)
"""
import os
from pydantic_settings import BaseSettings
from urllib.parse import urlparse, parse_qs


class Settings(BaseSettings):
    # Database URLs
    postgres_url: str = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/foodadvisor")
    
    # MongoDB - Hỗ trợ cả MongoDB Atlas và local MongoDB
    # MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/dbname?retryWrites=true&w=majority
    # Local MongoDB: mongodb://localhost:27017/
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME", "foodadvisor")
    
    # API keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
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

