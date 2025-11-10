"""
Pydantic models cho foods - Ẩm thực Việt Nam
"""
from pydantic import BaseModel
from typing import Optional, List


class Food(BaseModel):
    """Model cho thực phẩm/món ăn Việt Nam"""
    id: Optional[int] = None
    name: str  # Tên món (VD: "Phở bò", "Cơm tấm sườn nướng")
    name_vn: str  # Tên tiếng Việt
    name_en: Optional[str] = None  # Tên tiếng Anh (nếu có)
    
    # Thông tin phân loại
    category: Optional[str] = None  # Nhóm món: "phở", "bún", "cơm", "gỏi", "bánh", "canh", etc.
    region: Optional[str] = None  # Vùng miền: "Bắc", "Trung", "Nam", "Miền Tây", etc.
    meal_type: Optional[str] = None  # Loại bữa: "sáng", "trưa", "tối", "xế"
    
    # Dinh dưỡng (per 100g)
    calories: float
    protein: Optional[float] = None  # g
    fat: Optional[float] = None  # g
    carbs: Optional[float] = None  # g
    fiber: Optional[float] = None  # g
    sodium: Optional[float] = None  # mg
    
    # Thành phần chính
    main_ingredients: Optional[List[str]] = None  # ["thịt bò", "bánh phở", "hành lá"]
    
    # Khẩu phần Việt Nam
    typical_serving_g: Optional[float] = None  # Khẩu phần điển hình (gram)
    typical_serving_desc: Optional[str] = None  # "1 tô phở trung bình"


class FoodNutritionResponse(BaseModel):
    """Response cho phân tích dinh dưỡng"""
    food_name: str
    identified_ingredients: List[str]
    estimated_weight_g: float
    nutrition: Food
    total_calories: float

