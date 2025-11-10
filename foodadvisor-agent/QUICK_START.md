# 🚀 Quick Start Guide

## ✅ Đã hoàn thành

1. ✅ Code đã sẵn sàng
2. ✅ Dependencies đã cài đặt
3. ✅ File `.env` đã được tạo với format đúng

## 📝 Các bước tiếp theo

### Bước 1: Cập nhật file `.env`

Mở file `.env` và cập nhật các giá trị sau:

#### 1.1 MongoDB Atlas Connection String

```env
MONGO_URL=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/foodadvisor?retryWrites=true&w=majority
```

**Lấy connection string:**
1. Đăng nhập [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Vào **Connect** → **Connect your application**
3. Copy connection string
4. Thay `<password>` và `<database>` bằng thông tin của bạn

**Cấu hình Network Access:**
- Vào **Network Access** → **Add IP Address**
- Thêm `0.0.0.0/0` (cho phép tất cả IP) hoặc IP cụ thể

#### 1.2 PostgreSQL Connection String

```env
POSTGRES_URL=postgresql://username:password@host:port/database_name
```

**Nếu dùng PostgreSQL local:**
```env
POSTGRES_URL=postgresql://fooduser:foodpass@localhost:5432/foodadvisor
```

**Nếu dùng PostgreSQL cloud:**
- AWS RDS: `postgresql://user:pass@your-db.region.rds.amazonaws.com:5432/foodadvisor`
- Azure: `postgresql://user:pass@your-server.postgres.database.azure.com:5432/foodadvisor`

#### 1.3 OpenAI API Key

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Lấy tại: https://platform.openai.com/api-keys

### Bước 2: Khởi tạo PostgreSQL Database

```bash
python setup_database.py
```

Script này sẽ:
- Tạo các bảng trong PostgreSQL
- Load dữ liệu mẫu (món ăn Việt Nam: Phở bò, Cơm tấm, Gỏi cuốn)

### Bước 3: Kiểm tra kết nối

```bash
python test_connections.py
```

Kiểm tra:
- ✅ PostgreSQL connection
- ✅ MongoDB Atlas connection
- ✅ Tất cả modules import OK

### Bước 4: Chạy server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Bước 5: Test API

Mở browser: **http://localhost:8000/docs**

Hoặc test bằng curl:
```bash
# Test root endpoint
curl http://localhost:8000/

# Test popular recipes
curl http://localhost:8000/suggest-recipe/popular-vietnamese
```

## 📋 Checklist

- [ ] Cập nhật `MONGO_URL` trong `.env` với MongoDB Atlas connection string
- [ ] Cập nhật `POSTGRES_URL` trong `.env` với PostgreSQL connection string
- [ ] Cập nhật `OPENAI_API_KEY` trong `.env`
- [ ] Cấu hình Network Access trên MongoDB Atlas
- [ ] Chạy `python setup_database.py` để khởi tạo database
- [ ] Chạy `python test_connections.py` để kiểm tra
- [ ] Chạy `uvicorn app.main:app --reload` để start server

## 🎯 Test nhanh không cần database

Nếu bạn muốn test nhanh mà chưa setup database:

```bash
# Chạy server
uvicorn app.main:app --reload

# Test endpoint không cần database
curl http://localhost:8000/suggest-recipe/popular-vietnamese
```

Một số endpoints có thể chạy mà không cần database (sẽ trả về dữ liệu mẫu hoặc lỗi).

## 📚 Tài liệu thêm

- `UPDATE_ENV_GUIDE.md` - Hướng dẫn chi tiết cập nhật .env
- `SETUP_GUIDE.md` - Hướng dẫn setup đầy đủ
- `README.md` - Tài liệu chính của dự án

## ❓ Troubleshooting

### Lỗi kết nối MongoDB Atlas
- Kiểm tra Network Access trên Atlas dashboard
- Kiểm tra username/password trong connection string
- Kiểm tra database name có đúng không

### Lỗi kết nối PostgreSQL
- Kiểm tra PostgreSQL đang chạy
- Kiểm tra username/password
- Kiểm tra database đã được tạo chưa

### Lỗi import modules
- Chạy: `pip install -r requirements.txt`
- Kiểm tra Python version: `python --version` (nên dùng 3.11+)

