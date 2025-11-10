"""
PyMongo client - Hỗ trợ MongoDB Atlas và Local MongoDB
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Khởi tạo MongoDB client (lazy initialization)
_client = None
_db = None

def _init_mongo_connection():
    """
    Khởi tạo kết nối MongoDB (lazy initialization)
    """
    global _client, _db
    
    if _client is not None:
        return
    
    try:
        # Kết nối MongoDB (hỗ trợ cả Atlas và local)
        mongo_url = settings.mongo_url
        
        if not mongo_url:
            logger.warning("⚠️  MONGO_URL không được cấu hình trong .env")
            return
        
        # Nếu MongoDB Atlas, đảm bảo connection string đúng format
        if "mongodb+srv://" in mongo_url or "mongodb://" in mongo_url:
            # Connection options cho MongoDB Atlas
            connection_options = {
                "serverSelectionTimeoutMS": 5000,
                "connectTimeoutMS": 10000,
                "socketTimeoutMS": 45000
            }
            
            # Parse và thêm options nếu chưa có (tránh override options có sẵn trong URL)
            if "mongodb+srv://" in mongo_url and "?" not in mongo_url:
                # Thêm connection options nếu là Atlas và chưa có options
                mongo_url = f"{mongo_url}?retryWrites=true&w=majority"
            
            _client = MongoClient(mongo_url, **connection_options)
            
            # Test connection
            _client.admin.command('ping')
            logger.info("✅ Kết nối MongoDB thành công")
            
            # Lấy database name từ settings
            db_name = settings.get_mongo_db_name()
            _db = _client[db_name]
            logger.info(f"📊 Sử dụng database: {db_name}")
            
            # Log loại kết nối
            if "mongodb+srv://" in mongo_url:
                logger.info("☁️  Đang sử dụng MongoDB Atlas (Cloud)")
            else:
                logger.info("💻 Đang sử dụng MongoDB Local")
            
        else:
            logger.warning("⚠️  MongoDB connection string không hợp lệ")
            raise ConfigurationError("MongoDB connection string không hợp lệ")
            
    except ConnectionFailure as e:
        logger.error(f"❌ Không thể kết nối MongoDB: {str(e)}")
        logger.warning("Đảm bảo MongoDB connection string trong .env đúng format")
        logger.warning("Đối với MongoDB Atlas: mongodb+srv://username:password@cluster.net/dbname?retryWrites=true&w=majority")
        # Không raise để app vẫn có thể chạy mà không cần MongoDB
    except ConfigurationError as e:
        logger.error(f"❌ Cấu hình MongoDB không hợp lệ: {str(e)}")
        # Không raise để app vẫn có thể chạy mà không cần MongoDB
    except Exception as e:
        logger.error(f"❌ Lỗi khi khởi tạo MongoDB: {str(e)}")
        # Không raise để app vẫn có thể chạy mà không cần MongoDB


def get_mongo_db():
    """
    Lấy MongoDB database instance (lazy initialization)
    """
    if _db is None:
        _init_mongo_connection()
    
    if _db is None:
        raise ConnectionFailure("MongoDB chưa được kết nối. Kiểm tra MONGO_URL trong .env")
    return _db


def get_mongo_client():
    """
    Lấy MongoDB client instance (lazy initialization)
    """
    if _client is None:
        _init_mongo_connection()
    
    if _client is None:
        raise ConnectionFailure("MongoDB client chưa được khởi tạo. Kiểm tra MONGO_URL trong .env")
    return _client


def test_connection() -> bool:
    """
    Test kết nối MongoDB
    """
    try:
        if _client is None:
            _init_mongo_connection()
        
        if _client is None:
            return False
        
        _client.admin.command('ping')
        return True
    except Exception:
        return False

