"""
Models cho hồ sơ người dùng
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserProfile(BaseModel):
    """Hồ sơ người dùng"""
    id: Optional[int] = None
    user_id: str
    
    # Thông tin cơ bản
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None  # "Nam", "Nữ"
    
    # Thể trạng
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    
    # Mục tiêu sức khỏe
    health_goals: Optional[List[str]] = None  # ["Giảm cân", "Tăng cơ", "Duy trì"]
    target_weight: Optional[float] = None
    
    # Bệnh lý
    diseases: Optional[List[str]] = None  # ["Tiểu đường", "Huyết áp cao"]
    
    # Vùng miền và sở thích
    region: Optional[str] = None  # "Bắc", "Trung", "Nam"
    food_preferences: Optional[List[str]] = None  # Món ăn yêu thích
    food_allergies: Optional[List[str]] = None
    
    # Thông tin calo
    daily_calorie_target: Optional[float] = None
    activity_level: Optional[str] = None  # "Ít vận động", "Trung bình", "Nhiều"
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

