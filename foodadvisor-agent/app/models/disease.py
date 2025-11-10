"""
Models cho rules bệnh lý phổ biến tại Việt Nam
"""
from pydantic import BaseModel
from typing import Optional, List


class DiseaseRule(BaseModel):
    """Rules dinh dưỡng cho bệnh lý"""
    id: Optional[int] = None
    disease_name: str  # "Tiểu đường", "Mỡ máu cao", "Huyết áp cao", "Gout", etc.
    disease_name_en: Optional[str] = None
    
    # Thực phẩm được phép
    allowed_foods: Optional[List[str]] = None  # Danh sách tên món/thực phẩm
    allowed_categories: Optional[List[str]] = None  # Danh sách nhóm món được phép
    
    # Thực phẩm cần hạn chế/tránh
    restricted_foods: Optional[List[str]] = None
    restricted_categories: Optional[List[str]] = None
    
    # Giới hạn dinh dưỡng
    max_calories_per_meal: Optional[float] = None
    max_calories_per_day: Optional[float] = None
    min_protein_per_meal: Optional[float] = None
    max_carbs_per_meal: Optional[float] = None
    max_fat_per_meal: Optional[float] = None
    max_sodium_per_day: Optional[float] = None  # mg
    
    # Lời khuyên đặc biệt
    recommendations: Optional[List[str]] = None  # Lời khuyên cụ thể
    vietnamese_specific_advice: Optional[str] = None  # Lời khuyên riêng cho ẩm thực Việt


class HealthAdviceRequest(BaseModel):
    """Request cho tư vấn sức khỏe"""
    user_profile: Optional[dict] = None  # Thông tin người dùng
    diseases: List[str]  # Danh sách bệnh lý
    analyzed_foods: List[str]  # Danh sách món ăn đã phân tích
    daily_calories: Optional[float] = None


class HealthAdviceResponse(BaseModel):
    """Response cho tư vấn sức khỏe"""
    recommendations: List[str]
    warnings: List[str]
    suitable_foods: List[str]
    avoid_foods: List[str]
    dietary_score: float  # Điểm đánh giá (0-100)

