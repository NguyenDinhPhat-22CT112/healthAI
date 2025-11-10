"""
SQLAlchemy models cho PostgreSQL - Ẩm thực Việt Nam
Schema mới: foods, diseases_rules, users, user_diseases, user_meals, user_preferences
"""
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, ARRAY, Date, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class User(Base):
    """Bảng Users - Hồ sơ người dùng"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    
    full_name = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)  # 'Nam', 'Nữ', 'Khác'
    
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)  # Computed column
    
    activity_level = Column(String(20), default='Trung bình', nullable=True)  # 'Ít vận động', 'Nhẹ', 'Trung bình', 'Nặng', 'Rất nặng'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    diseases = relationship("UserDisease", back_populates="user", cascade="all, delete-orphan")
    meals = relationship("UserMeal", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Food(Base):
    """Bảng Foods - Thực phẩm từ foodData.xlsx"""
    __tablename__ = "foods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    
    # Dinh dưỡng (per 100g)
    glucid = Column(Float, nullable=True)  # Glucid (g/100g)
    fiber = Column(Float, nullable=True)   # Chất xơ (g/100g)
    lipid = Column(Float, nullable=True)   # Lipid (g/100g)
    protid = Column(Float, nullable=True)  # Protid (g/100g)
    calo = Column(Float, nullable=True)     # Calo (kcal/100g)
    
    # JSONB fields
    vitamins = Column(JSONB, nullable=True)  # {vitA: 1, vitB1: 0.11, ...}
    tags = Column(JSONB, default={}, nullable=True)  # {'low_lipid': true, 'vietnamese': true}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Recipe(Base):
    """Bảng Recipes - Công thức món ăn Việt Nam"""
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String(200), nullable=False, index=True)
    name_vn = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=True)
    
    category = Column(String(100), nullable=False, index=True)
    region = Column(String(50), nullable=True, index=True)
    difficulty = Column(String(50), nullable=True)
    cooking_time_minutes = Column(Integer, nullable=True)
    servings = Column(Integer, nullable=True)
    
    # Dinh dưỡng (per serving)
    calories_per_serving = Column(Float, nullable=True)
    protein_per_serving = Column(Float, nullable=True)
    fat_per_serving = Column(Float, nullable=True)
    carbs_per_serving = Column(Float, nullable=True)
    
    # Ingredients và steps lưu dạng JSON
    ingredients_json = Column(Text, nullable=True)  # JSON string
    steps_json = Column(Text, nullable=True)  # JSON string
    
    tags = Column(ARRAY(String), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DiseaseRule(Base):
    """Bảng Diseases Rules - Rules dinh dưỡng cho bệnh lý"""
    __tablename__ = "diseases_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    disease = Column(String(100), unique=True, nullable=False, index=True)
    
    # JSONB constraints: {'max_lipid': 15, 'min_fiber': 8, ...}
    constraints = Column(JSONB, nullable=False)
    
    avoid_foods = Column(ARRAY(String), default=[], nullable=True)
    recommend_foods = Column(ARRAY(String), default=[], nullable=True)
    
    priority_level = Column(String(20), default='medium', nullable=True)  # 'high' cho ba bệnh chính
    notes = Column(Text, nullable=True)
    
    is_custom = Column(Boolean, default=False, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class UserDisease(Base):
    """Bảng User Diseases - Bệnh lý của người dùng"""
    __tablename__ = "user_diseases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    disease_name = Column(String(100), nullable=False)
    
    diagnosed_at = Column(Date, nullable=True)
    severity = Column(String(20), default='Trung bình', nullable=True)  # 'Nhẹ', 'Trung bình', 'Nặng'
    is_primary = Column(Boolean, default=False, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="diseases")
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class UserMeal(Base):
    """Bảng User Meals - Nhật ký bữa ăn của người dùng"""
    __tablename__ = "user_meals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    meal_name = Column(String(200), nullable=True)
    image_mongo_id = Column(String(100), nullable=True)  # ObjectId từ MongoDB
    
    captured_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    total_calories = Column(Float, nullable=True)
    glucid = Column(Float, nullable=True)
    lipid = Column(Float, nullable=True)
    protid = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    
    suitability = Column(JSONB, nullable=True)  # { "Mỡ trong máu": 8.5, "Béo phì": 6.2 }
    
    feedback_rating = Column(Integer, nullable=True)  # 1-5
    feedback_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meals")


class UserPreference(Base):
    """Bảng User Preferences - Sở thích và mục tiêu người dùng"""
    __tablename__ = "user_preferences"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    
    cuisine_style = Column(String(50), default='Việt Nam', nullable=True)  # 'Miền Bắc', 'Miền Trung', 'Miền Nam', 'Quốc tế', 'Chay'
    avoid_ingredients = Column(ARRAY(String), nullable=True)  # ['đậu phụ', 'hành tây']
    favorite_ingredients = Column(ARRAY(String), nullable=True)  # ['cá basa', 'rau muống']
    
    meal_frequency = Column(JSONB, default={"breakfast": True, "lunch": True, "dinner": True, "snack": False}, nullable=True)
    calorie_goal_daily = Column(Integer, default=1800, nullable=True)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")

