"""
Script kiểm tra và validate MongoDB Atlas connection string
"""
import sys
import re
from urllib.parse import urlparse, unquote

def validate_mongo_url(connection_string: str):
    """
    Validate MongoDB Atlas connection string format
    
    Args:
        connection_string: MongoDB connection string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not connection_string:
        return False, "Connection string không được để trống"
    
    # Kiểm tra format cơ bản
    if not connection_string.startswith("mongodb+srv://") and not connection_string.startswith("mongodb://"):
        return False, "Connection string phải bắt đầu với 'mongodb+srv://' hoặc 'mongodb://'"
    
    # Kiểm tra placeholder
    placeholders = ["your_username", "your_password", "your_cluster", "<username>", "<password>", "<cluster>"]
    for placeholder in placeholders:
        if placeholder in connection_string:
            return False, f"Connection string vẫn chứa placeholder: {placeholder}"
    
    # Parse connection string
    try:
        if connection_string.startswith("mongodb+srv://"):
            # MongoDB Atlas format: mongodb+srv://user:pass@cluster.net/db?options
            pattern = r"mongodb\+srv://([^:]+):([^@]+)@([^/]+)/([^?]+)(\?.*)?"
            match = re.match(pattern, connection_string)
            
            if not match:
                return False, "Connection string không đúng format MongoDB Atlas"
            
            username, password, cluster, database, options = match.groups()
            
            # Kiểm tra các thành phần
            if not username or username.strip() == "":
                return False, "Username không được để trống"
            
            if not password or password.strip() == "":
                return False, "Password không được để trống"
            
            if not cluster or cluster.strip() == "":
                return False, "Cluster name không được để trống"
            
            if not database or database.strip() == "":
                return False, "Database name không được để trống"
            
            # Kiểm tra cluster name
            if not cluster.endswith(".mongodb.net"):
                return False, f"Cluster name không đúng format (phải kết thúc bằng .mongodb.net): {cluster}"
            
            # Decode password để kiểm tra
            try:
                decoded_password = unquote(password)
            except:
                decoded_password = password
            
            return True, f"✅ Connection string hợp lệ!\n   Username: {username}\n   Cluster: {cluster}\n   Database: {database}\n   Has options: {options is not None}"
            
        else:
            # MongoDB local format: mongodb://user:pass@host:port/db?options
            parsed = urlparse(connection_string)
            
            if not parsed.username or not parsed.password:
                return False, "Connection string thiếu username hoặc password"
            
            if not parsed.hostname:
                return False, "Connection string thiếu hostname"
            
            return True, f"✅ Connection string hợp lệ (MongoDB Local)!\n   Host: {parsed.hostname}\n   Port: {parsed.port or '27017'}\n   Database: {parsed.path.lstrip('/') if parsed.path else 'default'}"
            
    except Exception as e:
        return False, f"Lỗi khi parse connection string: {str(e)}"

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔍 MongoDB Atlas Connection String Validator")
    print("="*60)
    
    # Đọc từ .env nếu không có argument
    if len(sys.argv) > 1:
        connection_string = sys.argv[1]
    else:
        try:
            from app.config import settings
            connection_string = settings.mongo_url
            print(f"\n📝 Đang kiểm tra connection string từ .env...")
        except Exception as e:
            print(f"❌ Không thể đọc connection string từ .env: {str(e)}")
            print("\n💡 Sử dụng:")
            print("   python validate_mongo_url.py 'mongodb+srv://user:pass@cluster.net/db?options'")
            sys.exit(1)
    
    print(f"\n📋 Connection string: {connection_string[:80]}...")
    
    # Validate
    is_valid, message = validate_mongo_url(connection_string)
    
    print(f"\n{'='*60}")
    if is_valid:
        print("✅ KẾT QUẢ: Connection string hợp lệ!")
        print(f"\n{message}")
        print("\n💡 Bước tiếp theo:")
        print("   1. Kiểm tra IP whitelist trên MongoDB Atlas")
        print("   2. Test kết nối: python test_mongo_connection.py")
        print("   3. Chạy app: uvicorn app.main:app --reload")
    else:
        print("❌ KẾT QUẢ: Connection string không hợp lệ!")
        print(f"\n❌ Lỗi: {message}")
        print("\n💡 Hướng dẫn:")
        print("   1. Lấy connection string từ MongoDB Atlas:")
        print("      - Đăng nhập https://www.mongodb.com/cloud/atlas")
        print("      - Vào Connect → Connect your application")
        print("      - Copy connection string")
        print("   2. Thay thế <username>, <password>, <cluster> bằng giá trị thực tế")
        print("   3. Thêm database name sau cluster: /foodadvisor")
        print("   4. Cập nhật file .env với connection string đã sửa")
        print("\n📝 Format chuẩn:")
        print("   mongodb+srv://username:password@cluster.mongodb.net/foodadvisor?retryWrites=true&w=majority")
        sys.exit(1)

