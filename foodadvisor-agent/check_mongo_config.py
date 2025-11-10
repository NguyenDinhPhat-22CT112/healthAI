"""
Script kiểm tra cấu hình MongoDB
"""
from app.config import settings

def check_mongo_config():
    """Kiểm tra cấu hình MongoDB"""
    print("\n" + "="*60)
    print("🔍 Kiểm tra cấu hình MongoDB")
    print("="*60)
    
    mongo_url = settings.mongo_url
    mongo_db_name = settings.mongo_db_name
    
    print(f"\n📝 MONGO_URL: {mongo_url}")
    print(f"📝 MONGO_DB_NAME: {mongo_db_name}")
    
    # Phân tích loại MongoDB
    if "mongodb+srv://" in mongo_url:
        print("\n✅ Đang sử dụng: MongoDB Atlas (Cloud)")
        print("   - Format: mongodb+srv://username:password@cluster.net/dbname")
        
        # Parse connection string
        try:
            parts = mongo_url.split("@")
            if len(parts) > 1:
                cluster_part = parts[1].split("/")[0]
                print(f"   - Cluster: {cluster_part}")
        except:
            pass
        
    elif "mongodb://" in mongo_url:
        if "localhost" in mongo_url or "127.0.0.1" in mongo_url:
            print("\n⚠️  Đang sử dụng: MongoDB Local")
            print("   - Format: mongodb://localhost:27017/")
            print("\n💡 Để chuyển sang MongoDB Atlas:")
            print("   1. Đăng nhập MongoDB Atlas: https://www.mongodb.com/cloud/atlas")
            print("   2. Vào Connect → Connect your application")
            print("   3. Copy connection string")
            print("   4. Cập nhật file .env với format:")
            print("      MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/foodadvisor?retryWrites=true&w=majority")
        else:
            print("\n⚠️  Đang sử dụng: MongoDB (Remote)")
            print(f"   - Host: {mongo_url}")
    else:
        print("\n❌ MongoDB connection string không hợp lệ")
    
    # Kiểm tra database name
    db_name_from_url = settings.get_mongo_db_name()
    print(f"\n📂 Database name được sử dụng: {db_name_from_url}")
    
    # Kiểm tra kết nối
    print("\n" + "="*60)
    print("🔌 Kiểm tra kết nối...")
    print("="*60)
    
    try:
        from app.database.mongo import test_connection
        if test_connection():
            print("✅ Kết nối MongoDB thành công!")
        else:
            print("❌ Không thể kết nối MongoDB")
            print("\n💡 Nguyên nhân có thể:")
            if "mongodb+srv://" in mongo_url:
                print("   - IP whitelist chưa được cấu hình trên Atlas")
                print("   - Username/password sai")
                print("   - Network connection issues")
            else:
                print("   - MongoDB local chưa được khởi động")
                print("   - Port 27017 không mở")
                print("   - Hoặc cần chuyển sang MongoDB Atlas")
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra kết nối: {str(e)}")

if __name__ == "__main__":
    check_mongo_config()

