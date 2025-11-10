# Hướng dẫn chạy FastAPI Server

## ❌ Lỗi hiện tại

Khi chạy `uvicorn app.main:app --reload`, xuất hiện lỗi:
```
ModuleNotFoundError: No module named 'app'
```

**Nguyên nhân:** Uvicorn đang chạy từ thư mục cha (`D:\Code\HealthAI`) thay vì `foodadvisor-agent`

## ✅ Giải pháp

### Cách 1: Chạy từ đúng thư mục (Khuyến nghị)

**Bước 1:** Chuyển vào thư mục dự án:
```bash
cd D:\Code\HealthAI\foodadvisor-agent
```

**Bước 2:** Chạy uvicorn:
```bash
uvicorn app.main:app --reload
```

### Cách 2: Sử dụng script Python

Chạy script `run_server.py`:
```bash
python run_server.py
```

Script này sẽ tự động:
- Đảm bảo đang ở đúng thư mục
- Set PYTHONPATH đúng
- Chạy uvicorn với cấu hình phù hợp

### Cách 3: Chạy với PYTHONPATH

Nếu phải chạy từ thư mục cha:
```bash
# Windows PowerShell
$env:PYTHONPATH="D:\Code\HealthAI\foodadvisor-agent"
uvicorn app.main:app --reload

# Hoặc
cd D:\Code\HealthAI\foodadvisor-agent
uvicorn app.main:app --reload
```

### Cách 4: Chạy với đường dẫn đầy đủ

```bash
uvicorn app.main:app --reload --app-dir D:\Code\HealthAI\foodadvisor-agent
```

## 🚀 Chạy Server

### 1. Kiểm tra thư mục hiện tại
```bash
pwd
# Phải là: D:\Code\HealthAI\foodadvisor-agent
```

### 2. Kiểm tra module có thể import
```bash
python -c "from app.main import app; print('✅ OK')"
```

### 3. Chạy server
```bash
# Cách 1: Uvicorn trực tiếp
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Cách 2: Sử dụng script
python run_server.py
```

### 4. Test API
Mở browser: **http://127.0.0.1:8000/docs**

## 📋 Checklist

- [ ] Đang ở đúng thư mục: `D:\Code\HealthAI\foodadvisor-agent`
- [ ] Module `app` có thể import: `python -c "import app"`
- [ ] FastAPI app có thể import: `python -c "from app.main import app"`
- [ ] Uvicorn đã được cài đặt: `pip install uvicorn[standard]`
- [ ] Server chạy thành công: `uvicorn app.main:app --reload`

## ⚠️ Lưu ý

1. **Luôn chạy từ thư mục `foodadvisor-agent`**
   - Không chạy từ thư mục cha `HealthAI`
   - Đảm bảo thư mục `app` có trong thư mục hiện tại

2. **Nếu vẫn gặp lỗi:**
   - Kiểm tra file `app/__init__.py` có tồn tại không
   - Kiểm tra file `app/main.py` có tồn tại không
   - Kiểm tra PYTHONPATH

3. **Watch directory:**
   - Uvicorn sẽ watch `D:\Code\HealthAI` nếu chạy từ thư mục cha
   - Nên chạy từ `foodadvisor-agent` để watch đúng thư mục

## 🎯 Test sau khi chạy

1. **Root endpoint:**
   ```bash
   curl http://127.0.0.1:8000/
   ```

2. **API Docs:**
   - Browser: http://127.0.0.1:8000/docs

3. **Health check:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```

