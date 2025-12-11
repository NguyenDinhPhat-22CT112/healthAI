"""
SQLAlchemy Models - Complete Database Schema for PostgreSQL
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, Date, Numeric, ARRAY, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

# Define ENUM types
gender_enum = ENUM('male', 'female', 'other', name='gender')
activity_level_enum = ENUM('sedentary', 'light', 'moderate', 'active', 'very_active', name='activity_level')
goal_type_enum = ENUM('lose_weight', 'maintain', 'gain_weight', 'muscle_gain', name='goal_type')
meal_type_enum = ENUM('breakfast', 'lunch', 'dinner', 'snack', name='meal_type')
severity_level_enum = ENUM('mild', 'moderate', 'severe', 'life_threatening', name='severity_level')
difficulty_level_enum = ENUM('easy', 'medium', 'hard', name='difficulty_level')


class User(Base):
    """User model - Thông tin người dùng"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, unique=True, nullable=False, index=True)
    username = Column(Text, unique=True, nullable=False, index=True)
    full_name = Column(Text)
    password_hash = Column(Text, nullable=False)
    avatar_url = Column(Text)
    gender = Column(gender_enum)
    birth_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user_settings = relationship("UserSettings", back_populates="user", uselist=False)
    health_profile = relationship("HealthProfile", back_populates="user", uselist=False)
    nutrition_goals = relationship("NutritionGoals", back_populates="user", uselist=False)
    medical_conditions = relationship("UserMedicalCondition", back_populates="user")
    allergies = relationship("UserAllergy", back_populates="user")
    medications = relationship("Medication", back_populates="user")
    meals = relationship("Meal", back_populates="user")
    recipes = relationship("Recipe", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    health_logs = relationship("HealthLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    image_analyses = relationship("ImageAnalysis", back_populates="user")
    diet_plans = relationship("UserDietPlan", back_populates="user")
    meal_plans = relationship("MealPlan", back_populates="user")


class UserSettings(Base):
    """User Settings - Cài đặt người dùng"""
    __tablename__ = "user_settings"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    theme = Column(Text, default='light')
    language = Column(Text, default='vi')
    notifications_enabled = Column(Boolean, default=True)
    measurement_system = Column(Text, default='metric')
    
    # Relationships
    user = relationship("User", back_populates="user_settings")


class HealthProfile(Base):
    """Health Profile - Hồ sơ sức khỏe"""
    __tablename__ = "health_profiles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    weight_kg = Column(Numeric(5,2), nullable=False)
    height_cm = Column(Numeric(5,2), nullable=False)
    activity_level = Column(activity_level_enum, default='moderate')
    # BMI will be computed column in PostgreSQL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="health_profile")


class NutritionGoals(Base):
    """Nutrition Goals - Mục tiêu dinh dưỡng"""
    __tablename__ = "nutrition_goals"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    goal_type = Column(goal_type_enum, nullable=False)
    daily_calories = Column(Integer)
    daily_protein_grams = Column(Integer)
    daily_carb_grams = Column(Integer)
    daily_fat_grams = Column(Integer)
    condition_specific = Column(JSON)
    weekly_weight_change_kg = Column(Numeric(4,2))
    target_date = Column(Date)
    
    # Relationships
    user = relationship("User", back_populates="nutrition_goals")


# Medical Conditions
class MedicalCondition(Base):
    """Medical Conditions - Danh mục bệnh lý"""
    __tablename__ = "medical_conditions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    code = Column(Text, unique=True)
    description = Column(Text)
    recommended_diet_type = Column(Text)
    warnings = Column(Text)
    recommended_calories_multiplier = Column(Numeric(4,3), default=1.0)
    
    # Relationships
    user_conditions = relationship("UserMedicalCondition", back_populates="condition")
    disease_recommendations = relationship("DiseaseRecommendation", back_populates="condition")


class UserMedicalCondition(Base):
    """User Medical Conditions - Bệnh lý của người dùng"""
    __tablename__ = "user_medical_conditions"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    condition_id = Column(UUID(as_uuid=True), ForeignKey("medical_conditions.id"), primary_key=True)
    severity = Column(severity_level_enum, default='moderate')
    diagnosed_at = Column(Date)
    
    # Relationships
    user = relationship("User", back_populates="medical_conditions")
    condition = relationship("MedicalCondition", back_populates="user_conditions")


# Allergies
class Allergy(Base):
    """Allergies - Danh mục dị ứng"""
    __tablename__ = "allergies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    
    # Relationships
    user_allergies = relationship("UserAllergy", back_populates="allergy")


class UserAllergy(Base):
    """User Allergies - Dị ứng của người dùng"""
    __tablename__ = "user_allergies"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    allergy_id = Column(UUID(as_uuid=True), ForeignKey("allergies.id"), primary_key=True)
    severity = Column(severity_level_enum, nullable=False)
    diagnosed_at = Column(Date)
    
    # Relationships
    user = relationship("User", back_populates="allergies")
    allergy = relationship("Allergy", back_populates="user_allergies")


class Medication(Base):
    """Medications - Thuốc"""
    __tablename__ = "medications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    dosage = Column(Text)
    frequency = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Relationships
    user = relationship("User", back_populates="medications")


# Nutrition Core
class Unit(Base):
    """Units - Đơn vị đo lường"""
    __tablename__ = "units"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    abbreviation = Column(Text, nullable=False)
    to_gram_factor = Column(Numeric, nullable=False)


class Nutrient(Base):
    """Nutrients - Chất dinh dưỡng"""
    __tablename__ = "nutrients"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    unit = Column(Text, nullable=False)
    
    # Relationships
    food_nutrients = relationship("FoodNutrient", back_populates="nutrient")
    disease_recommendations = relationship("DiseaseRecommendation", back_populates="nutrient")


class Food(Base):
    """Foods - Thực phẩm"""
    __tablename__ = "foods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    category = Column(Text)
    calories_per_100g = Column(Numeric(6,2), nullable=False)
    barcode = Column(Text, unique=True)
    is_verified = Column(Boolean, default=False)
    high_glycemic = Column(Boolean, default=False)
    high_sodium = Column(Boolean, default=False)
    image_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    nutrients = relationship("FoodNutrient", back_populates="food")
    meal_foods = relationship("MealFood", back_populates="food")
    recipe_ingredients = relationship("RecipeIngredient", back_populates="food")


class FoodNutrient(Base):
    """Food Nutrients - Dinh dưỡng thực phẩm"""
    __tablename__ = "food_nutrients"
    
    food_id = Column(UUID(as_uuid=True), ForeignKey("foods.id", ondelete="CASCADE"), primary_key=True)
    nutrient_id = Column(Integer, ForeignKey("nutrients.id"), primary_key=True)
    amount_per_100g = Column(Numeric, nullable=False)
    
    # Relationships
    food = relationship("Food", back_populates="nutrients")
    nutrient = relationship("Nutrient", back_populates="food_nutrients")


class DiseaseRecommendation(Base):
    """Disease Recommendations - Khuyến nghị dinh dưỡng theo bệnh"""
    __tablename__ = "disease_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condition_id = Column(UUID(as_uuid=True), ForeignKey("medical_conditions.id", ondelete="CASCADE"), nullable=False)
    nutrient_id = Column(Integer, ForeignKey("nutrients.id"), nullable=False)
    recommended_daily_min = Column(Numeric)
    recommended_daily_max = Column(Numeric)
    notes = Column(Text)
    
    __table_args__ = (
        CheckConstraint('condition_id IS NOT NULL AND nutrient_id IS NOT NULL', name='unique_condition_nutrient'),
    )
    
    # Relationships
    condition = relationship("MedicalCondition", back_populates="disease_recommendations")
    nutrient = relationship("Nutrient", back_populates="disease_recommendations")


# Meals & Logging
class Meal(Base):
    """Meals - Bữa ăn"""
    __tablename__ = "meals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    meal_type = Column(meal_type_enum, nullable=False)
    meal_date = Column(Date, nullable=False)
    eaten_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meals")
    foods = relationship("MealFood", back_populates="meal")


class MealFood(Base):
    """Meal Foods - Thực phẩm trong bữa ăn"""
    __tablename__ = "meal_foods"
    
    meal_id = Column(UUID(as_uuid=True), ForeignKey("meals.id", ondelete="CASCADE"), primary_key=True)
    food_id = Column(UUID(as_uuid=True), ForeignKey("foods.id"), primary_key=True)
    quantity_grams = Column(Numeric, nullable=False)
    displayed_quantity = Column(Numeric)
    displayed_unit_id = Column(Integer, ForeignKey("units.id"))
    
    # Relationships
    meal = relationship("Meal", back_populates="foods")
    food = relationship("Food", back_populates="meal_foods")
    unit = relationship("Unit")


# Recipes
class Recipe(Base):
    """Recipes - Công thức nấu ăn"""
    __tablename__ = "recipes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    name = Column(Text, nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    prep_time_mins = Column(Integer, default=0)
    cook_time_mins = Column(Integer, default=0)
    # total_time_mins will be computed column in PostgreSQL
    servings = Column(Integer, default=1)
    difficulty = Column(difficulty_level_enum, default='medium')
    cuisine = Column(Text)
    is_public = Column(Boolean, default=False)
    suitable_for_conditions = Column(ARRAY(Text), default=[])
    image_url = Column(Text)
    average_rating = Column(Numeric(3,2), default=0)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recipes")
    ingredients = relationship("RecipeIngredient", back_populates="recipe")
    ratings = relationship("RecipeRating", back_populates="recipe")


class RecipeIngredient(Base):
    """Recipe Ingredients - Nguyên liệu công thức"""
    __tablename__ = "recipe_ingredients"
    
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    food_id = Column(UUID(as_uuid=True), ForeignKey("foods.id"), primary_key=True)
    quantity = Column(Numeric, nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"))
    
    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")
    food = relationship("Food", back_populates="recipe_ingredients")
    unit = relationship("Unit")


class RecipeRating(Base):
    """Recipe Ratings - Đánh giá công thức"""
    __tablename__ = "recipe_ratings"
    
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
    review = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recipe = relationship("Recipe", back_populates="ratings")
    user = relationship("User")


# AI & Chat
class ChatSession(Base):
    """Chat Sessions - Phiên chat"""
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    """Chat Messages - Tin nhắn chat"""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(Text, CheckConstraint("role IN ('user', 'assistant', 'system')"), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class ImageAnalysis(Base):
    """Image Analyses - Phân tích hình ảnh"""
    __tablename__ = "image_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(Text, nullable=False)
    detected_foods = Column(JSON)
    confidence = Column(Numeric(5,4))
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="image_analyses")


# Diet Plans
class UserDietPlan(Base):
    """User Diet Plans - Kế hoạch ăn uống từ AI"""
    __tablename__ = "user_diet_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, default='Kế hoạch từ AI')
    primary_condition_id = Column(UUID(as_uuid=True), ForeignKey("medical_conditions.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    daily_calories = Column(Integer)
    notes = Column(JSON)
    generated_by_agent = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="diet_plans")
    primary_condition = relationship("MedicalCondition")


class MealPlan(Base):
    """Meal Plans - Kế hoạch bữa ăn thủ công"""
    __tablename__ = "meal_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meal_plans")
    days = relationship("MealPlanDay", back_populates="meal_plan")


class MealPlanDay(Base):
    """Meal Plan Days - Chi tiết kế hoạch theo ngày"""
    __tablename__ = "meal_plan_days"
    
    meal_plan_id = Column(UUID(as_uuid=True), ForeignKey("meal_plans.id", ondelete="CASCADE"), primary_key=True)
    meal_date = Column(Date, primary_key=True)
    meal_type = Column(meal_type_enum, primary_key=True)
    suggested_recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id"))
    actual_meal_id = Column(UUID(as_uuid=True), ForeignKey("meals.id"))
    
    # Relationships
    meal_plan = relationship("MealPlan", back_populates="days")
    suggested_recipe = relationship("Recipe")
    actual_meal = relationship("Meal")


# Logs & Notifications
class HealthLog(Base):
    """Health Logs - Nhật ký sức khỏe"""
    __tablename__ = "health_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    log_date = Column(Date, nullable=False)
    weight_kg = Column(Numeric(5,2))
    energy_level = Column(Integer, CheckConstraint('energy_level >= 1 AND energy_level <= 10'))
    sleep_hours = Column(Numeric(4,2))
    blood_glucose_mgdl = Column(Numeric(5,1))
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="health_logs")


class Notification(Base):
    """Notifications - Thông báo"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    body = Column(Text)
    type = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
