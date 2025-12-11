# Database Structure

This document outlines the database structure for the Food Advisor Agent application.

## Overview

The application uses PostgreSQL as the primary database to store user data, food information, recipes, medical conditions, and chat interactions. The schema is designed to support comprehensive health-aware food recommendations.

## Database Schema

```sql
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ENUM Types
CREATE TYPE gender AS ENUM ('male', 'female', 'other');
CREATE TYPE activity_level AS ENUM ('sedentary', 'light', 'moderate', 'active', 'very_active');
CREATE TYPE goal_type AS ENUM ('lose_weight', 'maintain', 'gain_weight', 'muscle_gain');
CREATE TYPE meal_type AS ENUM ('breakfast', 'lunch', 'dinner', 'snack');
CREATE TYPE severity_level AS ENUM ('mild', 'moderate', 'severe', 'life_threatening');
CREATE TYPE difficulty_level AS ENUM ('easy', 'medium', 'hard');

-- 1. USERS & PROFILES
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT,
    password_hash TEXT NOT NULL,
    avatar_url TEXT,
    gender gender,
    birth_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_settings (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    theme TEXT DEFAULT 'light',
    language TEXT DEFAULT 'vi',
    notifications_enabled BOOLEAN DEFAULT true,
    measurement_system TEXT DEFAULT 'metric' -- metric/imperial
);

CREATE TABLE health_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    weight_kg NUMERIC(5,2) NOT NULL,
    height_cm NUMERIC(5,2) NOT NULL,
    activity_level activity_level DEFAULT 'moderate',
    bmi NUMERIC(4,2) GENERATED ALWAYS AS (ROUND((weight_kg / ((height_cm/100)^2))::numeric, 2)) STORED,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE nutrition_goals (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    goal_type goal_type NOT NULL,
    daily_calories INT,
    daily_protein_grams INT,
    daily_carb_grams INT,
    daily_fat_grams INT,
    condition_specific JSONB, -- {"tiểu_đường": {"max_carbs": 150}, "huyết_áp_cao": {"max_sodium_mg": 1500}}
    weekly_weight_change_kg NUMERIC(4,2),
    target_date DATE
);

-- 2. MEDICAL CONDITIONS & RECOMMENDATIONS (RẤT QUAN TRỌNG CHO AGENT)
CREATE TABLE medical_conditions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,                    -- Tiểu đường type 2, Cao huyết áp, Béo phì...
    code TEXT UNIQUE,                             -- diabetes_t2, hypertension, obesity
    description TEXT,
    recommended_die meal_foods)
recipes ←→ foods (qua recipe_ingredients)
```

## Sơ đồ ERD chính

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    users    │────│ health_profiles  │    │ nutrition_goals │
│             │    │                  │    │                 │
│ - id (PK)   │    │ - user_id (FK)   │    │ - user_id (FK)  │
│ - email     │    │ - weight         │    │ - daily_calories│
│ - username  │    │ - height         │    │ - daily_protein │
│ - full_name │    │ - bmi            │    │ - goal_type     │
└─────────────┘    └──────────────────┘    └─────────────────┘
       │
       ├─────────────────────────────────────────────────────────┐
       │                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ food_allergies  │    │    medications   │    │   health_logs   │
│                 │    │                  │    │                 │
│ - user_id (FK)  │    │ - user_id (FK)   │    │ - user_id (FK)  │
│ - allergen_name │    │ - name           │    │ - log_date      │
│ - severity      │    │ - dosage         │    │ - weight        │
└─────────────────┘    └──────────────────┘    └─────────────────┘

┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    meals    │────│   meal_foods     │────│     foods       │
│             │    │                  │    │                 │
│ - id (PK)   │    │ - meal_id (FK)   │    │ - id (PK)       │
│ - user_id   │    │ - food_id (FK)   │    │ - name          │
│ - meal_type │    │ - quantity       │    │ - category      │
│ - meal_date │    │ - calories       │    │ - calories_100g │
└─────────────┘    └──────────────────┘    └─────────────────┘

┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   recipes   │────│recipe_ingredients│────│     foods       │
│             │    │                  │    │                 │
│ - id (PK)   │    │ - recipe_id (FK) │    │ (same as above) │
│ - user_id   │    │ - food_id (FK)   │    │                 │
│ - name      │    │ - quantity       │    │                 │
│ - difficulty│    │ - unit           │    │                 │
└─────────────┘    └──────────────────┘    └─────────────────┘
       │
       │           ┌──────────────────┐
       └───────────│ recipe_ratings   │
                   │                  │
                   │ - recipe_id (FK) │
                   │ - user_id (FK)   │
                   │ - rating         │
                   └──────────────────┘
```

## Ràng buộc và quy tắc

### Primary Keys
- Tất cả bảng sử dụng UUID làm primary key
- Tự động generate bằng `uuid_generate_v4()`

### Foreign Keys
- Cascade delete cho hầu hết quan hệ user
- Set null cho một số quan hệ không bắt buộc

### Unique Constraints
```sql
users: email, username
user_medical_conditions: (user_id, condition_id)
food_allergies: (user_id, allergen_name)
recipe_ratings: (recipe_id, user_id)
```

### Check Constraints
```sql
users.gender: IN ('male', 'female', 'other')
health_profiles.activity_level: IN ('sedentary', 'light', 'moderate', 'active', 'very_active')
medical_conditions.severity: IN ('mild', 'moderate', 'severe')
food_allergies.severity: IN ('mild', 'moderate', 'severe', 'life_threatening')
recipe_ratings.rating: BETWEEN 1 AND 5
health_logs.energy_level: BETWEEN 1 AND 10
```

### Generated Columns
```sql
health_profiles.bmi: Tự động tính từ weight và height
recipes.total_time: prep_time + cook_time
```

## Indexes quan trọng

### Performance Indexes
```sql
-- User lookups
idx_users_email, idx_users_username

-- Date-based queries
idx_meals_user_date (user_id, meal_date)
idx_health_logs_user_date (user_id, log_date)

-- Food searches
idx_foods_name, idx_foods_category, idx_foods_barcode

-- Recipe searches
idx_recipes_public, idx_recipes_rating, idx_recipes_cuisine
```

## Triggers và Functions

### Auto-update timestamps
```sql
update_updated_at_column(): Tự động cập nhật updated_at
```

### Business logic functions
```sql
calculate_bmi(weight, height): Tính BMI
get_bmi_category(bmi): Phân loại BMI
calculate_daily_calories(): Tính nhu cầu calo hàng ngày
```

## Views hữu ích

### user_health_summary
Tổng hợp thông tin sức khỏe người dùng

### daily_nutrition_summary  
Tổng hợp dinh dưỡng theo ngày

### recipe_details
Công thức với thông tin đánh giá

## Dữ liệu mẫu

Database bao gồm:
- 3 bệnh lý phổ biến (tiểu đường, cao huyết áp, béo phì)
- 8 thực phẩm cơ bản (cơm, thịt, rau, cá, trứng, bánh mì, chuối)
- Cấu hình dinh dưỡng và hạn chế cho từng bệnh lý

## Mở rộng tương lai

### Bảng có thể thêm:
- **exercise_logs** - Nhật ký tập luyện
- **meal_plans** - Kế hoạch ăn uống
- **food_brands** - Thương hiệu thực phẩm
- **nutritionist_consultations** - Tư vấn chuyên gia
- **social_features** - Tính năng xã hội (follow, share)

### Tối ưu hóa:
- Partitioning cho bảng lớn (meals, health_logs)
- Materialized views cho báo cáo
- Full-text search cho foods và recipes
- Caching layer cho queries thường dùng