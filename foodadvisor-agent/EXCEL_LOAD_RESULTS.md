# Kết quả Load Excel Dataset

## ✅ Đã hoàn thành

### 1. File Excel
- **File:** `data/foodData.xlsx`
- **Số dòng:** 273 records
- **Format:** Vietnamese column names với vitamins

### 2. Script đã được cập nhật
- ✅ `generate_inserts.py` - Map Vietnamese columns sang English
- ✅ `data_loader.py` - Load Excel vào PostgreSQL với xử lý:
  - Map Vietnamese column names
  - Xử lý range format "125/171" (lấy giá trị đầu tiên)
  - Skip existing records để tránh duplicate
  - Parse vitamins thành JSONB

### 3. Database
- ✅ **Tổng số foods:** 274 records
- ✅ **Sample data:**
  - Bánh mì đen: 250 calo/100g
  - Bánh mì: 266 calo/100g
  - Bí xanh (baby): 21 calo/100g
  - Bí xanh (mùa hè): 16 calo/100g
  - Bí đao: 14 calo/100g

## 📋 Column Mapping

Excel Vietnamese → Database English:
- `Tên thực phẩm` → `name`
- `Glucid` → `glucid`
- `Chất Xơ` → `fiber`
- `Lipid (Béo)` → `lipid`
- `Protid (Đạm)` → `protid`
- `Calo` → `calo`
- `Vitamin A` → `vitA`
- `Vitamin B1` → `vitB1`
- `Vitamin B2` → `vitB2`
- `Vitamin B3` → `vitB3`
- `Vitamin B6` → `vitB6`
- `Vitamin B9` → `vitB9`
- `Vitamin B12` → `vitB12`
- `Vitamin C` → `vitC`
- `Vitamin D` → `vitD`
- `Vitamin E` → `vitE`
- `Vitamin K` → `vitK`
- `Vitamin H (B7)` → `vitH`

## 🚀 Cách sử dụng

### 1. Load Excel vào PostgreSQL
```bash
python -c "from app.utils.data_loader import load_excel_to_postgres; load_excel_to_postgres('data/foodData.xlsx', 'foods')"
```

### 2. Generate SQL INSERTs
```bash
python app/utils/generate_inserts.py data/foodData.xlsx inserts_foods.sql
```

### 3. Kiểm tra số lượng foods
```bash
python -c "from app.database.postgres import SessionLocal; from app.database.models import Food; db = SessionLocal(); print(f'Total: {db.query(Food).count()}'); db.close()"
```

## ✅ Features

1. **Auto column mapping** - Tự động map Vietnamese columns sang English
2. **Range handling** - Xử lý giá trị dạng "125/171" (lấy giá trị đầu tiên)
3. **Skip existing** - Tự động skip records đã tồn tại
4. **Vitamins JSONB** - Parse vitamins thành JSONB format
5. **Error handling** - Xử lý lỗi và rollback khi cần

## 📊 Kết quả

- ✅ **274 foods** đã được load vào database
- ✅ **Tất cả vitamins** đã được parse thành JSONB
- ✅ **Không có duplicate** records
- ✅ **Tên tiếng Việt** được lưu đúng format

## 🎯 Next Steps

1. Test API endpoints với data mới:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Test query foods:
   ```bash
   curl http://localhost:8000/calculate-calories/
   ```

3. Kiểm tra trong database:
   ```sql
   SELECT name, calo, glucid, lipid, protid FROM foods LIMIT 10;
   ```

