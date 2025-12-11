-- PostgreSQL Schema cho Health AI - Ẩm thực Việt Nam

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table Foods (từ foodData.xlsx)
CREATE TABLE IF NOT EXISTS foods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,  -- e.g., 'Bánh mì đen'
    glucid FLOAT,                       -- Glucid (g/100g)
    fiber FLOAT,                        -- Chất xơ (g/100g)
    lipid FLOAT,                        -- Lipid (g/100g)
    protid FLOAT,                       -- Protid (g/100g)
    calo FLOAT,                         -- Calo (kcal/100g)
    vitamins JSONB,                     -- {vitA: 1, vitB1: 0.11, ...}
    tags JSONB DEFAULT '{}'::JSONB,     -- e.g., {'low_lipid': true, 'vietnamese': true}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index cho query nhanh
CREATE INDEX IF NOT EXISTS idx_foods_name ON foods(name);
CREATE INDEX IF NOT EXISTS idx_foods_calo ON foods(calo);
CREATE INDEX IF NOT EXISTS idx_foods_lipid ON foods(lipid);

-- Table Diseases Rules (focus ba bệnh chính, linh hoạt cho khác)
CREATE TABLE IF NOT EXISTS diseases_rules (
    id SERIAL PRIMARY KEY,
    disease VARCHAR(100) UNIQUE NOT NULL,  -- e.g., 'Mỡ trong máu'
    constraints JSONB NOT NULL,            -- e.g., {'max_lipid': 15, 'min_fiber': 8}
    avoid_foods TEXT[] DEFAULT '{}',       -- Array: ['mỡ bò', 'ba chỉ lợn']
    recommend_foods TEXT[] DEFAULT '{}',   -- Array: ['cá basa', 'rau muống']
    priority_level VARCHAR(20) DEFAULT 'medium',  -- 'high' cho ba bệnh chính
    notes TEXT,                            -- Giải thích Việt Nam focus
    is_custom BOOLEAN DEFAULT FALSE,
    user_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index
CREATE INDEX IF NOT EXISTS idx_diseases_disease ON diseases_rules(disease);

-- Insert Rules cho ba bệnh chính (hardcode, dựa trên Vinmec/Bộ Y tế 2025)
INSERT INTO diseases_rules (disease, constraints, avoid_foods, recommend_foods, priority_level, notes) VALUES
('Mỡ trong máu', '{"max_lipid": 15, "min_omega3": 0.5, "min_fiber": 8, "max_glucid": 40}'::JSONB, 
 ARRAY['mỡ bò', 'ba chỉ lợn', 'dừa cùi'], ARRAY['cá basa', 'bí đỏ', 'hạt chia', 'yến mạch'], 'high', 
 'Ưu tiên omega-3 từ cá sông, chất xơ từ rau củ địa phương.')
ON CONFLICT (disease) DO NOTHING;

INSERT INTO diseases_rules (disease, constraints, avoid_foods, recommend_foods, priority_level, notes) VALUES
('Béo phì', '{"max_calo": 450, "max_glucid": 40, "min_protid": 20, "min_fiber": 7}'::JSONB, 
 ARRAY['gạo trắng', 'bánh mì kẹp', 'thức ăn nhanh'], ARRAY['rau muống', 'ức gà', 'khoai lang', 'rau bina'], 'high', 
 'Giảm tinh bột tinh chế, tăng rau quả; khẩu phần nhỏ cho người Việt.')
ON CONFLICT (disease) DO NOTHING;

INSERT INTO diseases_rules (disease, constraints, avoid_foods, recommend_foods, priority_level, notes) VALUES
('Tăng huyết áp', '{"max_sodium": 400, "min_kali": 1000, "min_fiber": 7, "lipid_max": 10}'::JSONB, 
 ARRAY['nước mắm mặn', 'thịt hun khói', 'mì gói'], ARRAY['cải thìa', 'cam', 'cà chua', 'khoai lang'], 'high', 
 'DASH-style: Ít muối, giàu kali từ trái cây múi; tránh gia vị mặn phổ biến.')
ON CONFLICT (disease) DO NOTHING;

-- Table Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,  -- bcrypt hash
    full_name VARCHAR(100),
    age INT CHECK (age >= 13),
    gender VARCHAR(10) CHECK (gender IN ('Nam', 'Nữ', 'Khác')),
    height_cm FLOAT CHECK (height_cm > 0),
    weight_kg FLOAT CHECK (weight_kg > 0),
    bmi FLOAT GENERATED ALWAYS AS (weight_kg / ((height_cm / 100) ^ 2)) STORED,
    activity_level VARCHAR(20) DEFAULT 'Trung bình' 
        CHECK (activity_level IN ('Ít vận động', 'Nhẹ', 'Trung bình', 'Nặng', 'Rất nặng')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Index tìm kiếm nhanh
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Table User Diseases
CREATE TABLE IF NOT EXISTS user_diseases (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    disease_name VARCHAR(100) NOT NULL,  -- 'Mỡ trong máu', 'Tiểu đường',...
    diagnosed_at DATE,
    severity VARCHAR(20) DEFAULT 'Trung bình' 
        CHECK (severity IN ('Nhẹ', 'Trung bình', 'Nặng')),
    is_primary BOOLEAN DEFAULT FALSE,  -- Ưu tiên bệnh chính
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, disease_name)
);

-- Trigger: Chỉ 1 bệnh chính
CREATE OR REPLACE FUNCTION enforce_one_primary()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_primary THEN
        UPDATE user_diseases 
        SET is_primary = FALSE 
        WHERE user_id = NEW.user_id AND id != NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trig_one_primary ON user_diseases;
CREATE TRIGGER trig_one_primary
    BEFORE INSERT OR UPDATE ON user_diseases
    FOR EACH ROW EXECUTE FUNCTION enforce_one_primary();

-- Table User Meals
CREATE TABLE IF NOT EXISTS user_meals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    meal_name VARCHAR(200),
    image_mongo_id VARCHAR(100),  -- ObjectId từ MongoDB
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_calories FLOAT,
    glucid FLOAT, lipid FLOAT, protid FLOAT, fiber FLOAT,
    suitability JSONB,  -- { "Mỡ trong máu": 8.5, "Béo phì": 6.2 }
    feedback_rating INT CHECK (feedback_rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_meals_user ON user_meals(user_id);
CREATE INDEX IF NOT EXISTS idx_user_meals_date ON user_meals(captured_at);

-- Table User Preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    cuisine_style VARCHAR(50) DEFAULT 'Việt Nam' 
        CHECK (cuisine_style IN ('Miền Bắc', 'Miền Trung', 'Miền Nam', 'Quốc tế', 'Chay')),
    avoid_ingredients TEXT[],  -- ['đậu phụ', 'hành tây']
    favorite_ingredients TEXT[],  -- ['cá basa', 'rau muống']
    meal_frequency JSONB DEFAULT '{"breakfast": true, "lunch": true, "dinner": true, "snack": false}',
    calorie_goal_daily INT DEFAULT 1800,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Foreign key cho diseases_rules.user_id
ALTER TABLE diseases_rules ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

