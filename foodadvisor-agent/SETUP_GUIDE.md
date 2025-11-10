# Hướng dẫn Setup và Kiểm tra

## ✅ Đã hoàn thành

1. **Dependencies đã cài đặt thành công**
   - ✅ pandas 2.3.3 (tương thích Python 3.14)
   - ✅ pillow 12.0.0 (tương thích Python 3.14)
   - ✅ Tất cả packages khác đã cài đặt

2. **Code đã được cập nhật**
   - ✅ LangChain 1.0.3 compatibility (đã fix imports)
   - ✅ Tất cả modules import thành công
   - ✅ Tools đã tương thích với LangChain mới

## ⚠️ Cần thiết lập

### 1. PostgreSQL Database

**Lỗi hiện tại:** `password authentication failed for user "fooduser"`

**Giải pháp:**

#### Option A: Sử dụng PostgreSQL local đã có
Cập nhật file `.env` với thông tin PostgreSQL của bạn:
```env
POSTGRES_URL=postgresql://username:password@localhost:5432/your_database
```

#### Option B: Tạo database mới
```sql
-- Kết nối PostgreSQL với user postgres
CREATE DATABASE foodadvisor;
CREATE USER fooduser WITH PASSWORD 'foodpass';
GRANT ALL PRIVILEGES ON DATABASE foodadvisor TO fooduser;
```

#### Option C: Sử dụng Docker
```bash
docker-compose up -d postgres
```

Sau đó chạy:
```bash
python setup_database.py
```

### 2. MongoDB Atlas

**Lỗi hiện tại:** `connection refused` (vì đang dùng local MongoDB nhưng chưa chạy)

**Giải pháp:**

Cập nhật file `.env` với MongoDB Atlas connection string:
```env
MONGO_URL=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/foodadvisor?retryWrites=true&w=majority
MONGO_DB_NAME=foodadvisor
```

**Lấy connection string:**
1. Đăng nhập [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Vào **Connect** → **Connect your application**
3. Copy connection string và thay `<password>` và `<database>`

### 3. OpenAI API Key

Cập nhật file `.env`:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## 📝 Các bước tiếp theo

### Bước 1: Cấu hình .env
```bash
# Chỉnh sửa file .env với thông tin thực tế của bạn
```

### Bước 2: Khởi tạo PostgreSQL
```bash
# Nếu dùng Docker
docker-compose up -d postgres

# Hoặc setup database thủ công (xem ở trên)
# Sau đó chạy:
python setup_database.py
```

### Bước 3: Kiểm tra kết nối
```bash
python test_connections.py
```

### Bước 4: Chạy server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Bước 5: Test API
Mở browser: `http://localhost:8000/docs`

## 🧪 Test nhanh

### Test API không cần database:
```bash
# Test endpoint popular recipes (không cần database)
curl http://localhost:8000/suggest-recipe/popular-vietnamese
```

### Test với database:
```bash
# Test calculate calories
curl -X POST "http://localhost:8000/calculate-calories/" \
  -H "Content-Type: application/json" \
  -d '{"foods": [{"name": "Phở bò", "quantity": 1, "unit": "serving"}]}'
```

## 📊 Trạng thái hiện tại

- ✅ Code: OK
- ✅ Dependencies: OK  
- ✅ Imports: OK
- ⚠️ PostgreSQL: Cần cấu hình
- ⚠️ MongoDB: Cần cấu hình (Atlas hoặc local)
- ⚠️ OpenAI API: Cần cấu hình

## 🎯 Quick Start

Nếu bạn muốn test nhanh mà không cần database:

1. Chạy server:
```bash
uvicorn app.main:app --reload
```

2. Test endpoint không cần database:
```bash
# Mở browser
http://localhost:8000/docs

# Test popular recipes
http://localhost:8000/suggest-recipe/popular-vietnamese
```

Một số endpoints có thể chạy mà không cần database (sẽ trả về lỗi hoặc dữ liệu mẫu).

