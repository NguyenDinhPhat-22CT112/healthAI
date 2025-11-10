# Hướng dẫn kiểm tra MongoDB Atlas Connection String

## ✅ Kiểm tra Connection String

### 1. Format chuẩn MongoDB Atlas

Connection string MongoDB Atlas phải có format:
```
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

**Các thành phần:**
- `mongodb+srv://` - Protocol cho MongoDB Atlas
- `username:password` - Username và password MongoDB Atlas của bạn
- `cluster.mongodb.net` - Cluster name từ MongoDB Atlas (ví dụ: `cluster0.abc123.mongodb.net`)
- `database_name` - Tên database (ví dụ: `foodadvisor`)
- `?retryWrites=true&w=majority` - Connection options

### 2. Kiểm tra file .env

Mở file `.env` và kiểm tra:
```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/foodadvisor?retryWrites=true&w=majority
```

**Lưu ý:**
- Không được có `<password>` hoặc `your_username` - phải là giá trị thực tế
- Password có thể chứa ký tự đặc biệt (@, #, $, ...) - cần URL encode
- Cluster name phải là tên cluster thực tế từ MongoDB Atlas

### 3. Lấy Connection String từ MongoDB Atlas

**Bước 1:** Đăng nhập [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)

**Bước 2:** Vào **Connect** → **Connect your application**

**Bước 3:** Copy connection string mẫu:
```
mongodb+srv://<username>:<password>@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
```

**Bước 4:** Thay thế:
- `<username>` → username MongoDB Atlas của bạn
- `<password>` → password MongoDB Atlas của bạn (nếu có ký tự đặc biệt, cần URL encode)
- Thêm database name sau cluster: `/foodadvisor`

**Bước 5:** Cập nhật file `.env`:
```env
MONGO_URL=mongodb+srv://myuser:mypassword@cluster0.abc123.mongodb.net/foodadvisor?retryWrites=true&w=majority
MONGO_DB_NAME=foodadvisor
```

### 4. URL Encode Password

Nếu password có ký tự đặc biệt, cần URL encode:
- `@` → `%40`
- `#` → `%23`
- `$` → `%24`
- `%` → `%25`
- `&` → `%26`
- `+` → `%2B`
- `=` → `%3D`
- `?` → `%3F`

**Ví dụ:**
- Password: `P@ssw0rd#123`
- URL encoded: `P%40ssw0rd%23123`
- Connection string: `mongodb+srv://user:P%40ssw0rd%23123@cluster.net/db`

### 5. Cấu hình Network Access

**Bước 1:** Vào **Network Access** trên MongoDB Atlas

**Bước 2:** Click **Add IP Address**

**Bước 3:** Chọn:
- **Allow Access from Anywhere** (`0.0.0.0/0`) - cho development
- Hoặc thêm IP cụ thể của bạn

**Bước 4:** Click **Confirm**

### 6. Test Connection

**Cách 1: Sử dụng script test**
```bash
python test_mongo_connection.py
```

**Cách 2: Test với connection string trực tiếp**
```bash
python test_mongo_connection.py "mongodb+srv://username:password@cluster.mongodb.net/foodadvisor?retryWrites=true&w=majority"
```

**Cách 3: Sử dụng check_mongo_config.py**
```bash
python check_mongo_config.py
```

**Cách 4: Test từ Python**
```python
from app.database.mongo import test_connection
if test_connection():
    print("✅ Kết nối thành công!")
else:
    print("❌ Kết nối thất bại!")
```

## 🔍 Troubleshooting

### Lỗi: "The DNS query name does not exist"

**Nguyên nhân:**
- Connection string vẫn là placeholder (`your_username`, `your_password`, `your_cluster`)
- Cluster name không đúng
- Network connection issues

**Giải pháp:**
1. Kiểm tra connection string trong `.env` - đảm bảo không có placeholder
2. Kiểm tra cluster name - phải là tên cluster thực tế từ MongoDB Atlas
3. Kiểm tra internet connection

### Lỗi: "Authentication failed"

**Nguyên nhân:**
- Username/password sai
- Password có ký tự đặc biệt nhưng chưa URL encode

**Giải pháp:**
1. Kiểm tra username/password trong connection string
2. URL encode password nếu có ký tự đặc biệt
3. Reset password trên MongoDB Atlas nếu cần

### Lỗi: "IP not whitelisted"

**Nguyên nhân:**
- IP của bạn chưa được whitelist trên MongoDB Atlas

**Giải pháp:**
1. Vào **Network Access** trên MongoDB Atlas
2. Thêm IP của bạn hoặc `0.0.0.0/0` (cho development)
3. Đợi vài phút để thay đổi có hiệu lực

### Lỗi: "Database not found"

**Nguyên nhân:**
- Database name không đúng
- Database chưa được tạo

**Giải pháp:**
1. Kiểm tra database name trong connection string
2. MongoDB Atlas sẽ tự động tạo database khi có data đầu tiên
3. Hoặc tạo database thủ công trên MongoDB Atlas

## ✅ Checklist

- [ ] Connection string không có placeholder (`your_username`, `your_password`, `your_cluster`)
- [ ] Username/password đã được thay thế bằng giá trị thực tế
- [ ] Password có ký tự đặc biệt đã được URL encode
- [ ] Cluster name là tên cluster thực tế từ MongoDB Atlas
- [ ] Database name đã được thêm vào connection string (sau `/`)
- [ ] IP đã được whitelist trên MongoDB Atlas
- [ ] Connection string đã được cập nhật trong file `.env`
- [ ] Test connection thành công

## 📝 Ví dụ Connection String đúng

```
mongodb+srv://myuser:mypassword123@cluster0.abc123.mongodb.net/foodadvisor?retryWrites=true&w=majority
```

**Với password có ký tự đặc biệt:**
```
mongodb+srv://myuser:P%40ssw0rd%23123@cluster0.abc123.mongodb.net/foodadvisor?retryWrites=true&w=majority
```

## 🚀 Sau khi cấu hình đúng

1. Test connection:
   ```bash
   python test_mongo_connection.py
   ```

2. Test với app:
   ```bash
   python test_connections.py
   ```

3. Chạy server:
   ```bash
   uvicorn app.main:app --reload
   ```

