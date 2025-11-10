# Cập nhật Schema PostgreSQL - Tóm tắt

## ✅ Đã hoàn thành

### 1. SQLAlchemy Models (`app/database/models.py`)
- ✅ Cập nhật `Food` model (thay `FoodItem`) với JSONB cho vitamins và tags
- ✅ Cập nhật `DiseaseRule` model với JSONB constraints
- ✅ Tạo `User` model mới với UUID primary key
- ✅ Tạo `UserDisease` model cho bệnh lý người dùng
- ✅ Tạo `UserMeal` model cho nhật ký bữa ăn
- ✅ Tạo `UserPreference` model cho sở thích người dùng

### 2. Database Schema (`app/database/schema.sql`)
- ✅ Tạo file schema.sql với tất cả tables
- ✅ Enable UUID extension
- ✅ Tạo indexes cho performance
- ✅ Insert sample data cho 3 bệnh chính (Mỡ trong máu, Béo phì, Tăng huyết áp)

### 3. Data Loader (`app/utils/data_loader.py`)
- ✅ Cập nhật `_load_food_items()` để load Excel với format mới (vitamins JSONB)
- ✅ Cập nhật `_load_disease_rules()` để load với JSONB constraints
- ✅ Cập nhật `init_sample_data()` với format mới

### 4. Scripts hỗ trợ
- ✅ `app/utils/generate_inserts.py` - Generate SQL INSERTs từ Excel
- ✅ `app/utils/load_schema.py` - Load schema SQL vào PostgreSQL

### 5. Tools và Routes
- ✅ Cập nhật `DBQueryTool` để query `Food` model mới
- ✅ Cập nhật `calculate_calories` route để dùng `Food` model
- ✅ Cập nhật imports trong tất cả files

## 📋 Schema mới

### Bảng `foods` (thay `food_items`)
```sql
CREATE TABLE foods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    glucid FLOAT,      -- Glucid (g/100g)
    fiber FLOAT,       -- Chất xơ (g/100g)
    lipid FLOAT,       -- Lipid (g/100g)
    protid FLOAT,      -- Protid (g/100g)
    calo FLOAT,        -- Calo (kcal/100g)
    vitamins JSONB,    -- {vitA: 1, vitB1: 0.11, ...}
    tags JSONB,        -- {'low_lipid': true, 'vietnamese': true}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Bảng `diseases_rules` (cập nhật)
```sql
CREATE TABLE diseases_rules (
    id SERIAL PRIMARY KEY,
    disease VARCHAR(100) UNIQUE NOT NULL,
    constraints JSONB NOT NULL,        -- {'max_lipid': 15, 'min_fiber': 8}
    avoid_foods TEXT[],
    recommend_foods TEXT[],
    priority_level VARCHAR(20),
    notes TEXT,
    is_custom BOOLEAN DEFAULT FALSE,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Bảng `users` (mới - UUID)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    height_cm FLOAT,
    weight_kg FLOAT,
    bmi FLOAT GENERATED ALWAYS AS (weight_kg / ((height_cm / 100) ^ 2)) STORED,
    activity_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Bảng `user_diseases` (mới)
```sql
CREATE TABLE user_diseases (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    disease_name VARCHAR(100) NOT NULL,
    diagnosed_at DATE,
    severity VARCHAR(20),
    is_primary BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, disease_name)
);
```

### Bảng `user_meals` (mới)
```sql
CREATE TABLE user_meals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    meal_name VARCHAR(200),
    image_mongo_id VARCHAR(100),
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_calories FLOAT,
    glucid FLOAT, lipid FLOAT, protid FLOAT, fiber FLOAT,
    suitability JSONB,  -- { "Mỡ trong máu": 8.5, "Béo phì": 6.2 }
    feedback_rating INT CHECK (feedback_rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Bảng `user_preferences` (mới)
```sql
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    cuisine_style VARCHAR(50) DEFAULT 'Việt Nam',
    avoid_ingredients TEXT[],
    favorite_ingredients TEXT[],
    meal_frequency JSONB,
    calorie_goal_daily INT DEFAULT 1800,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Cách sử dụng

### 1. Load schema vào PostgreSQL
```bash
# Cách 1: Sử dụng script Python
python app/utils/load_schema.py

# Cách 2: Sử dụng psql trực tiếp
psql -d foodadvisor -f app/database/schema.sql
```

### 2. Generate SQL INSERTs từ Excel
```bash
# Đặt file Excel vào data/foodData.xlsx
python app/utils/generate_inserts.py data/foodData.xlsx inserts_foods.sql

# Sau đó chạy SQL file
psql -d foodadvisor -f inserts_foods.sql
```

### 3. Load dữ liệu từ Excel qua Python
```bash
python -c "from app.utils.data_loader import load_excel_to_postgres; load_excel_to_postgres('data/foodData.xlsx', 'foods')"
```

### 4. Khởi tạo dữ liệu mẫu
```bash
python setup_database.py
```

## 📝 Lưu ý

1. **UUID Extension**: PostgreSQL cần enable extension `uuid-ossp`:
   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```

2. **JSONB Fields**: 
   - `vitamins` trong `foods` table là JSONB
   - `constraints` trong `diseases_rules` là JSONB
   - `suitability` trong `user_meals` là JSONB
   - `meal_frequency` trong `user_preferences` là JSONB

3. **Foreign Keys**:
   - `user_diseases.user_id` → `users.id` (CASCADE)
   - `user_meals.user_id` → `users.id` (CASCADE)
   - `user_preferences.user_id` → `users.id` (CASCADE)
   - `diseases_rules.user_id` → `users.id` (nullable, cho custom rules)

4. **Triggers**:
   - Trigger `enforce_one_primary` đảm bảo chỉ 1 bệnh chính per user

## ✅ Checklist

- [x] Models đã được cập nhật
- [x] Schema SQL đã được tạo
- [x] Data loader đã được cập nhật
- [x] Tools đã được cập nhật
- [x] Routes đã được cập nhật
- [x] Scripts hỗ trợ đã được tạo
- [ ] Test với database thực tế (cần PostgreSQL connection)

