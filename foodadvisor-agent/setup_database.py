"""
Script khởi tạo database và load dữ liệu mẫu
"""
import sys
from app.database.postgres import init_db, SessionLocal
from app.utils.data_loader import init_sample_data
from sqlalchemy import text

def setup_postgres():
    """Khởi tạo PostgreSQL database"""
    print("\n" + "="*50)
    print("🗄️  Khởi tạo PostgreSQL Database...")
    print("="*50)
    
    try:
        # Tạo tables
        print("📋 Đang tạo các bảng...")
        init_db()
        print("✅ Đã tạo các bảng thành công!")
        
        # Kiểm tra tables
        with SessionLocal() as db:
            result = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            print(f"📋 Các bảng đã tạo: {', '.join(tables)}")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo database: {str(e)}")
        print("\n💡 Hướng dẫn:")
        print("   1. Đảm bảo PostgreSQL đang chạy")
        print("   2. Kiểm tra POSTGRES_URL trong file .env")
        print("   3. Tạo database và user nếu chưa có:")
        print("      CREATE DATABASE foodadvisor;")
        print("      CREATE USER fooduser WITH PASSWORD 'foodpass';")
        print("      GRANT ALL PRIVILEGES ON DATABASE foodadvisor TO fooduser;")
        return False

def load_sample_data():
    """Load dữ liệu mẫu"""
    print("\n" + "="*50)
    print("📦 Load dữ liệu mẫu...")
    print("="*50)
    
    try:
        init_sample_data()
        print("✅ Đã load dữ liệu mẫu thành công!")
        return True
    except Exception as e:
        print(f"⚠️  Lỗi khi load dữ liệu mẫu: {str(e)}")
        print("   (Có thể bỏ qua nếu muốn load từ Excel)")
        return False

if __name__ == "__main__":
    print("\n" + "🚀"*25)
    print("Health AI - Database Setup")
    print("🚀"*25)
    
    # Setup PostgreSQL
    postgres_ok = setup_postgres()
    
    if postgres_ok:
        # Load sample data
        load_sample_data()
        
        print("\n" + "="*50)
        print("✅ HOÀN TẤT!")
        print("="*50)
        print("\n📝 Bước tiếp theo:")
        print("   1. Cập nhật MONGO_URL trong .env với MongoDB Atlas connection string")
        print("   2. Cập nhật OPENAI_API_KEY trong .env")
        print("   3. Chạy server: uvicorn app.main:app --reload")
        print("   4. Mở browser: http://localhost:8000/docs")
    else:
        print("\n⚠️  Cần fix lỗi PostgreSQL trước khi tiếp tục")
        sys.exit(1)

