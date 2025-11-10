"""
Test MongoDB Atlas connection với connection string thực tế
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
import sys

def test_mongo_connection(connection_string: str = None):
    """
    Test MongoDB Atlas connection
    
    Args:
        connection_string: MongoDB Atlas connection string (nếu None, sẽ đọc từ .env)
    """
    print("\n" + "="*60)
    print("🔍 Test MongoDB Atlas Connection")
    print("="*60)
    
    # Đọc connection string
    if connection_string is None:
        from app.config import settings
        connection_string = settings.mongo_url
        print(f"\n📝 MONGO_URL từ .env: {connection_string[:80]}...")
    else:
        print(f"\n📝 MONGO_URL từ parameter: {connection_string[:80]}...")
    
    # Kiểm tra format
    if not connection_string:
        print("❌ MONGO_URL không được cấu hình")
        return False
    
    if "mongodb+srv://" not in connection_string and "mongodb://" not in connection_string:
        print("❌ Connection string không hợp lệ (thiếu mongodb:// hoặc mongodb+srv://)")
        return False
    
    # Test connection
    try:
        print("\n🔌 Đang thử kết nối MongoDB Atlas...")
        
        # Connection options
        connection_options = {
            "serverSelectionTimeoutMS": 5000,
            "connectTimeoutMS": 10000,
            "socketTimeoutMS": 45000
        }
        
        # Parse connection string để lấy database name
        if "mongodb+srv://" in connection_string:
            # MongoDB Atlas format
            parts = connection_string.split("@")
            if len(parts) > 1:
                cluster_part = parts[1].split("/")[0]
                print(f"   Cluster: {cluster_part}")
            
            # Lấy database name
            if "/" in connection_string:
                db_part = connection_string.split("/")[-1].split("?")[0]
                if db_part and db_part != "":
                    print(f"   Database: {db_part}")
        
        # Tạo client
        client = MongoClient(connection_string, **connection_options)
        
        # Test connection
        print("   Đang ping server...")
        result = client.admin.command('ping')
        print(f"   ✅ Ping thành công: {result}")
        
        # List databases
        print("\n📊 Danh sách databases:")
        databases = client.list_database_names()
        for db in databases[:10]:  # Hiển thị 10 databases đầu
            print(f"   - {db}")
        
        # Lấy database name
        from app.config import settings
        db_name = settings.get_mongo_db_name()
        print(f"\n📂 Database sẽ sử dụng: {db_name}")
        
        # Kiểm tra database
        db = client[db_name]
        collections = db.list_collection_names()
        print(f"\n📋 Collections trong database '{db_name}':")
        if collections:
            for col in collections:
                print(f"   - {col}")
        else:
            print("   (Chưa có collections)")
        
        print("\n✅ Kết nối MongoDB Atlas thành công!")
        client.close()
        return True
        
    except ConnectionFailure as e:
        print(f"\n❌ Lỗi kết nối: {str(e)}")
        print("\n💡 Nguyên nhân có thể:")
        print("   - IP whitelist chưa được cấu hình trên Atlas")
        print("   - Username/password sai trong connection string")
        print("   - Cluster không tồn tại hoặc connection string sai")
        return False
    except ConfigurationError as e:
        print(f"\n❌ Lỗi cấu hình: {str(e)}")
        print("\n💡 Nguyên nhân có thể:")
        print("   - Connection string không đúng format")
        print("   - Thiếu username/password")
        print("   - Thiếu database name trong connection string")
        return False
    except Exception as e:
        print(f"\n❌ Lỗi không xác định: {str(e)}")
        print(f"   Loại lỗi: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Có thể test với connection string từ command line
    connection_string = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("\n" + "🚀"*25)
    print("MongoDB Atlas Connection Test")
    print("🚀"*25)
    
    success = test_mongo_connection(connection_string)
    
    if success:
        print("\n✅ Test thành công!")
    else:
        print("\n❌ Test thất bại!")
        print("\n💡 Hướng dẫn:")
        print("   1. Kiểm tra connection string trong file .env")
        print("   2. Đảm bảo IP của bạn đã được whitelist trên MongoDB Atlas")
        print("   3. Kiểm tra username/password trong connection string")
        print("   4. Test với connection string trực tiếp:")
        print("      python test_mongo_connection.py 'mongodb+srv://user:pass@cluster.net/dbname?retryWrites=true&w=majority'")
        sys.exit(1)

