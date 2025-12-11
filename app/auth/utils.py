"""
Authentication Utilities - Helper functions for user management
"""
import uuid
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.database.models import User, HealthProfile
from app.auth.schemas import UserCreate
from app.auth.hashing import get_password_hash


def generate_username(email: str) -> str:
    """
    Generate unique username from email
    
    Args:
        email: User email address
        
    Returns:
        Generated username
    """
    base_username = email.split("@")[0].lower()
    
    # Remove special characters
    username = "".join(c for c in base_username if c.isalnum())
    
    # Add random suffix if too short
    if len(username) < 3:
        username += "".join(secrets.choice(string.digits) for _ in range(3))
    
    return username[:20]  # Limit length


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by email address
    
    Args:
        db: Database session
        email: Email address
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get user by username
    
    Args:
        db: Database session
        username: Username
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.username == username.lower()).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """
    Get user by ID
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create new user in database
    
    Args:
        db: Database session
        user_data: User creation data
        
    Returns:
        Created user object
    """
    # Generate unique ID
    user_id = str(uuid.uuid4())
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user object
    user = User(
        id=user_id,
        email=user_data.email.lower(),
        username=user_data.username.lower(),
        full_name=user_data.full_name,
        password_hash=hashed_password,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Save to database
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def update_user_last_login(db: Session, user_id: str) -> None:
    """
    Update user's last login timestamp
    
    Args:
        db: Database session
        user_id: User ID
    """
    user = get_user_by_id(db, user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.commit()


def is_email_available(db: Session, email: str) -> bool:
    """
    Check if email is available for registration
    
    Args:
        db: Database session
        email: Email address to check
        
    Returns:
        True if available, False if taken
    """
    return get_user_by_email(db, email) is None


def is_username_available(db: Session, username: str) -> bool:
    """
    Check if username is available for registration
    
    Args:
        db: Database session
        username: Username to check
        
    Returns:
        True if available, False if taken
    """
    return get_user_by_username(db, username) is None


def generate_verification_code() -> str:
    """
    Generate 6-digit verification code
    
    Returns:
        6-digit verification code string
    """
    return "".join(secrets.choice(string.digits) for _ in range(6))


def generate_reset_token() -> str:
    """
    Generate secure reset token
    
    Returns:
        Random reset token string
    """
    return secrets.token_urlsafe(32)


def calculate_bmi(weight: float, height: float) -> Optional[float]:
    """
    Calculate BMI (Body Mass Index)
    
    Args:
        weight: Weight in kg
        height: Height in cm
        
    Returns:
        BMI value or None if invalid input
    """
    if not weight or not height or weight <= 0 or height <= 0:
        return None
    
    height_m = height / 100  # Convert cm to meters
    bmi = weight / (height_m ** 2)
    
    return round(bmi, 1)


def get_bmi_category(bmi: float) -> str:
    """
    Get BMI category in Vietnamese
    
    Args:
        bmi: BMI value
        
    Returns:
        BMI category string
    """
    if bmi < 18.5:
        return "Thiếu cân"
    elif bmi < 25:
        return "Bình thường"
    elif bmi < 30:
        return "Thừa cân"
    else:
        return "Béo phì"


def calculate_daily_calories(
    weight: float, 
    height: float, 
    age: int, 
    gender: str, 
    activity_level: str
) -> Optional[int]:
    """
    Calculate daily calorie needs using Mifflin-St Jeor equation
    
    Args:
        weight: Weight in kg
        height: Height in cm
        age: Age in years
        gender: 'male' or 'female'
        activity_level: Activity level string
        
    Returns:
        Daily calorie needs or None if invalid input
    """
    if not all([weight, height, age, gender]) or weight <= 0 or height <= 0 or age <= 0:
        return None
    
    # Base Metabolic Rate (BMR)
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:  # female
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Activity multipliers
    activity_multipliers = {
        'sedentary': 1.2,      # Ít vận động
        'light': 1.375,        # Vận động nhẹ
        'moderate': 1.55,      # Vận động vừa
        'active': 1.725,       # Vận động nhiều
        'very_active': 1.9     # Vận động rất nhiều
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.2)
    daily_calories = bmr * multiplier
    
    return int(round(daily_calories))


def get_health_recommendations(diseases: list) -> dict:
    """
    Get health recommendations based on diseases
    
    Args:
        diseases: List of disease names
        
    Returns:
        Dictionary with recommendations
    """
    recommendations = {
        "dietary_restrictions": [],
        "recommended_foods": [],
        "foods_to_avoid": [],
        "exercise_tips": [],
        "general_advice": []
    }
    
    for disease in diseases:
        disease_lower = disease.lower()
        
        if "tiểu đường" in disease_lower or "diabetes" in disease_lower:
            recommendations["foods_to_avoid"].extend([
                "Đường trắng", "Bánh ngọt", "Nước ngọt", "Cơm trắng"
            ])
            recommendations["recommended_foods"].extend([
                "Rau xanh", "Cá", "Yến mạch", "Đậu"
            ])
            recommendations["general_advice"].append(
                "Chia nhỏ bữa ăn, kiểm tra đường huyết thường xuyên"
            )
        
        elif "huyết áp cao" in disease_lower or "hypertension" in disease_lower:
            recommendations["foods_to_avoid"].extend([
                "Muối", "Đồ hộp", "Thịt hun khói", "Nước mắm"
            ])
            recommendations["recommended_foods"].extend([
                "Chuối", "Rau bina", "Cá hồi", "Yến mạch"
            ])
            recommendations["general_advice"].append(
                "Hạn chế muối, tăng kali, tránh căng thẳng"
            )
        
        elif "béo phì" in disease_lower or "obesity" in disease_lower:
            recommendations["foods_to_avoid"].extend([
                "Đồ chiên", "Thức ăn nhanh", "Nước ngọt", "Bánh kẹo"
            ])
            recommendations["recommended_foods"].extend([
                "Rau củ", "Trái cây ít đường", "Ức gà", "Cá"
            ])
            recommendations["general_advice"].append(
                "Giảm calo, tăng vận động, uống nhiều nước"
            )
    
    # Remove duplicates
    for key in recommendations:
        if isinstance(recommendations[key], list):
            recommendations[key] = list(set(recommendations[key]))
    
    return recommendations