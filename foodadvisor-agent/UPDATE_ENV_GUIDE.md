# Hướng dẫn cập nhật file .env cho MongoDB Atlas và PostgreSQL

## 📝 File .env đã được cập nhật

File `.env` đã được tạo lại với format đúng cho MongoDB Atlas và PostgreSQL.

## 🔧 Các bước cập nhật

### 1. MongoDB Atlas Connection String

**Bước 1:** Đăng nhập [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)

**Bước 2:** Vào **Connect** → **Connect your application**

**Bước 3:** Copy connection string mẫu:
```
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

**Bước 4:** Cập nhật file `.env`:
```env
MONGO_URL=mongodb+srv://your_username:your_actual_password@your_cluster.mongodb.net/foodadvisor?retryWrites=true&w=majority
MONGO_DB_NAME=foodadvisor
```

**Lưu ý:**
- Thay `<username>` bằng username MongoDB Atlas của bạn
- Thay `<password>` bằng password MongoDB Atlas của bạn
- Thay `<cluster>` bằng cluster name của bạn (ví dụ: `cluster0.abc123`)
- Thêm database name vào sau cluster: `/foodadvisor`

**Bước 5:** Cấu hình Network Access trên Atlas:
- Vào **Network Access** → **Add IP Address**
- Thêm `0.0.0.0/0` (cho phép tất cả IP) hoặc IP cụ thể của bạn

### 2. PostgreSQL Connection String

**Nếu dùng PostgreSQL local:**
```env
POSTGRES_URL=postgresql://username:password@localhost:5432/foodadvisor
```

**Nếu dùng PostgreSQL cloud (AWS RDS, Azure, etc.):**
```env
POSTGRES_URL=postgresql://username:password@host.region.rds.amazonaws.com:5432/foodadvisor
```

**Ví dụ với các cloud provider:**
- **AWS RDS:** `postgresql://user:pass@your-db.region.rds.amazonaws.com:5432/foodadvisor`
- **Azure Database:** `postgresql://user:pass@your-server.postgres.database.azure.com:5432/foodadvisor`
- **Google Cloud SQL:** `postgresql://user:pass@your-instance-ip:5432/foodadvisor`

### 3. OpenAI API Key

**Bước 1:** Đăng nhập [OpenAI Platform](https://platform.openai.com/api-keys)

**Bước 2:** Tạo API key mới

**Bước 3:** Copy và cập nhật vào `.env`:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## ✅ Kiểm tra sau khi cập nhật

Chạy script kiểm tra:
```bash
python check_mongo_config.py
python test_connections.py
```

## 📋 Ví dụ file .env hoàn chỉnh

```env
# PostgreSQL
POSTGRES_URL=postgresql://fooduser:foodpass@localhost:5432/foodadvisor

# MongoDB Atlas
MONGO_URL=mongodb+srv://myuser:mypassword@cluster0.abc123.mongodb.net/foodadvisor?retryWrites=true&w=majority
MONGO_DB_NAME=foodadvisor

# OpenAI
OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz1234567890
```

## ⚠️ Lưu ý bảo mật

1. **KHÔNG commit file `.env` vào git**
   - File `.env` đã có trong `.gitignore`
   - Chỉ commit `.env.example`

2. **Bảo mật credentials:**
   - Không chia sẻ file `.env`
   - Không hardcode credentials trong code
   - Sử dụng environment variables trong production

3. **Database permissions:**
   - Tạo user riêng cho ứng dụng (không dùng admin)
   - Giới hạn quyền truy cập cần thiết

## 🚀 Sau khi cập nhật

1. **Khởi tạo database:**
   ```bash
   python setup_database.py
   ```

2. **Test kết nối:**
   ```bash
   python test_connections.py
   ```

3. **Chạy server:**
   ```bash
   uvicorn app.main:app --reload
   ```

