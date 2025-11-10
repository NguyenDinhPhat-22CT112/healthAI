"""
Script kiểm tra kết nối database
"""
import sys
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_postgres():
    """Test kết nối PostgreSQL"""
    print("\n" + "="*50)
    print("🔍 Kiểm tra kết nối PostgreSQL...")
    print("="*50)
    
    try:
        from app.database.postgres import engine, init_db, SessionLocal
        from sqlalchemy import text
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL kết nối thành công!")
            print(f"📊 PostgreSQL version: {version[:50]}...")
            
        # Test database
        with SessionLocal() as db:
            result = db.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"📂 Database: {db_name}")
            
            # Kiểm tra tables
            result = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"📋 Các bảng đã tồn tại: {', '.join(tables)}")
            else:
                print("⚠️  Chưa có bảng nào. Chạy init_db() để tạo bảng.")
                print("   python -c \"from app.database.postgres import init_db; init_db()\"")
                
        return True
    except Exception as e:
        print(f"❌ Lỗi kết nối PostgreSQL: {str(e)}")
        try:
            from app.config import settings
            print(f"🔧 Kiểm tra POSTGRES_URL trong .env: {settings.postgres_url[:50]}...")
        except:
            pass
        return False

def test_mongodb():
    """Test kết nối MongoDB"""
    print("\n" + "="*50)
    print("🔍 Kiểm tra kết nối MongoDB...")
    print("="*50)
    
    try:
        from app.database.mongo import test_connection as test_mongo, get_mongo_db
        from app.config import settings
        
        if test_mongo():
            print("✅ MongoDB kết nối thành công!")
            
            # Test database
            db = get_mongo_db()
            print(f"📂 Database: {db.name}")
            
            # List collections
            collections = db.list_collection_names()
            if collections:
                print(f"📋 Collections: {', '.join(collections)}")
            else:
                print("📋 Chưa có collection nào (sẽ tự động tạo khi insert data)")
                
            return True
        else:
            print("❌ Không thể kết nối MongoDB")
            print(f"🔧 Kiểm tra MONGO_URL trong .env: {settings.mongo_url[:50]}...")
            return False
    except Exception as e:
        print(f"❌ Lỗi kết nối MongoDB: {str(e)}")
        try:
            from app.config import settings
            print(f"🔧 Kiểm tra MONGO_URL trong .env")
        except:
            pass
        return False

def test_config():
    """Kiểm tra cấu hình"""
    print("\n" + "="*50)
    print("⚙️  Kiểm tra cấu hình...")
    print("="*50)
    
    try:
        from app.config import settings
        
        print(f"📝 POSTGRES_URL: {settings.postgres_url[:50]}...")
        print(f"📝 MONGO_URL: {settings.mongo_url[:50]}...")
        print(f"📝 MONGO_DB_NAME: {settings.mongo_db_name}")
        
        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            print(f"📝 OPENAI_API_KEY: ✅ Đã cấu hình")
        else:
            print(f"📝 OPENAI_API_KEY: ⚠️  Chưa cấu hình hoặc chưa thay đổi")
    except Exception as e:
        print(f"❌ Lỗi khi đọc cấu hình: {str(e)}")

def test_imports():
    """Kiểm tra import các module"""
    print("\n" + "="*50)
    print("📦 Kiểm tra import modules...")
    print("="*50)
    
    modules = [
        "app.main",
        "app.config",
        "app.database.postgres",
        "app.database.mongo",
        "app.routes.analyze_meal",
        "app.routes.calculate_calories",
        "app.routes.suggest_recipe",
        "app.agents.food_advisor_agent",
        "app.tools.vision_tool",
        "app.tools.db_query_tool",
        "app.tools.recipe_generator_tool",
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {str(e)}")
            failed.append(module)
    
    if failed:
        print(f"\n⚠️  {len(failed)} module(s) không thể import")
        return False
    else:
        print(f"\n✅ Tất cả modules import thành công!")
        return True

if __name__ == "__main__":
    print("\n" + "🚀"*25)
    print("Health AI - Database Connection Test")
    print("🚀"*25)
    
    # Test imports trước
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n⚠️  Có lỗi import modules. Kiểm tra lại code.")
        sys.exit(1)
    
    # Test config
    test_config()
    
    # Test database connections
    postgres_ok = test_postgres()
    mongo_ok = test_mongodb()
    
    print("\n" + "="*50)
    print("📊 TỔNG KẾT")
    print("="*50)
    print(f"✅ Import modules: OK" if imports_ok else "❌ Import modules: FAIL")
    print(f"PostgreSQL: {'✅ OK' if postgres_ok else '❌ FAIL'}")
    print(f"MongoDB: {'✅ OK' if mongo_ok else '❌ FAIL'}")
    
    if imports_ok and postgres_ok and mongo_ok:
        print("\n🎉 Tất cả đều OK! Hệ thống sẵn sàng chạy.")
        print("\n📝 Bước tiếp theo:")
        print("   1. Khởi tạo database tables: python -c \"from app.database.postgres import init_db; init_db()\"")
        print("   2. Load dữ liệu mẫu: python -c \"from app.utils.data_loader import init_sample_data; init_sample_data()\"")
        print("   3. Chạy server: uvicorn app.main:app --reload")
        sys.exit(0)
    else:
        print("\n⚠️  Có lỗi. Kiểm tra lại cấu hình trong .env file.")
        sys.exit(1)

