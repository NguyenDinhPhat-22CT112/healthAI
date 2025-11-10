# Kiểm tra MongoDB Atlas Connection String

## 📋 Tình trạng hiện tại

Script validation đã phát hiện connection string trong file `.env` vẫn chứa **placeholder values**:

```
MONGO_URL=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/foodadvisor?retryWrites=true&w=majority
```

## ✅ Bạn cần làm gì?

### Bước 1: Kiểm tra file .env

Mở file `.env` và kiểm tra dòng `MONGO_URL`:
```env
MONGO_URL=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/foodadvisor?retryWrites=true&w=majority
```

**Nếu vẫn thấy `your_username`, `your_password`, `your_cluster`** → Cần cập nhật!

### Bước 2: Lấy Connection String từ MongoDB Atlas

1. Đăng nhập [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Vào **Connect** → **Connect your application**
3. Copy connection string mẫu:
   ```
   mongodb+srv://<username>:<password>@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
   ```

### Bước 3: Cập nhật Connection String

Thay thế trong connection string:
- `<username>` → username MongoDB Atlas của bạn (ví dụ: `myuser`)
- `<password>` → password MongoDB Atlas của bạn (ví dụ: `mypassword123`)
- Cluster name → tên cluster thực tế (ví dụ: `cluster0.abc123.mongodb.net`)
- Thêm database name sau cluster: `/foodadvisor`

**Ví dụ connection string đúng:**
```env
MONGO_URL=mongodb+srv://myuser:mypassword123@cluster0.abc123.mongodb.net/foodadvisor?retryWrites=true&w=majority
```

### Bước 4: Lưu file .env

Sau khi cập nhật, **lưu file .env** và test lại:

```bash
# Test validation
python validate_mongo_url.py

# Test connection
python test_mongo_connection.py
```

## 🔍 Test Connection String

### Cách 1: Sử dụng script validation
```bash
python validate_mongo_url.py
```

### Cách 2: Test với connection string trực tiếp
```bash
python validate_mongo_url.py "mongodb+srv://username:password@cluster.mongodb.net/foodadvisor?retryWrites=true&w=majority"
```

### Cách 3: Test kết nối thực tế
```bash
python test_mongo_connection.py
```

## ⚠️ Lưu ý về Password

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

## ✅ Checklist

- [ ] Connection string không có placeholder (`your_username`, `your_password`, `your_cluster`)
- [ ] Username đã được thay thế bằng username thực tế
- [ ] Password đã được thay thế bằng password thực tế (và URL encode nếu có ký tự đặc biệt)
- [ ] Cluster name là tên cluster thực tế từ MongoDB Atlas
- [ ] Database name (`foodadvisor`) đã được thêm vào connection string
- [ ] File `.env` đã được lưu
- [ ] Test validation thành công: `python validate_mongo_url.py`
- [ ] Test connection thành công: `python test_mongo_connection.py`

## 📝 Format chuẩn MongoDB Atlas

```
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

**Các thành phần:**
- `mongodb+srv://` - Protocol cho MongoDB Atlas
- `username:password` - Username và password MongoDB Atlas
- `cluster.mongodb.net` - Cluster name (ví dụ: `cluster0.abc123.mongodb.net`)
- `database_name` - Tên database (ví dụ: `foodadvisor`)
- `?retryWrites=true&w=majority` - Connection options

## 🚀 Sau khi cập nhật đúng

1. Test validation:
   ```bash
   python validate_mongo_url.py
   ```

2. Test connection:
   ```bash
   python test_mongo_connection.py
   ```

3. Test với app:
   ```bash
   python test_connections.py
   ```

4. Chạy server:
   ```bash
   uvicorn app.main:app --reload
   ```

