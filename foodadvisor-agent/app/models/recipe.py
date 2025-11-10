"""
Models cho công thức món ăn Việt Nam
"""
from pydantic import BaseModel
from typing import Optional, List, Dict


class RecipeIngredient(BaseModel):
    """Nguyên liệu trong công thức"""
    name: str
    name_vn: str
    quantity: float
    unit: str  # "g", "ml", "cái", "tép", "muỗng canh", etc.
    preparation: Optional[str] = None  # "băm nhỏ", "thái lát", "cắt khúc"


class RecipeStep(BaseModel):
    """Bước nấu trong công thức"""
    step_number: int
    instruction: str
    duration_minutes: Optional[int] = None
    tips: Optional[str] = None


class Recipe(BaseModel):
    """Công thức món ăn Việt Nam"""
    id: Optional[int] = None
    name: str
    name_vn: str
    name_en: Optional[str] = None
    
    # Phân loại
    category: str  # "phở", "bún", "cơm", "gỏi", etc.
    region: Optional[str] = None  # "Bắc", "Trung", "Nam"
    difficulty: Optional[str] = None  # "Dễ", "Trung bình", "Khó"
    cooking_time_minutes: Optional[int] = None
    servings: Optional[int] = None  # Số phần ăn
    
    # Dinh dưỡng (per serving)
    calories_per_serving: Optional[float] = None
    protein_per_serving: Optional[float] = None
    fat_per_serving: Optional[float] = None
    carbs_per_serving: Optional[float] = None
    
    # Nguyên liệu và cách làm
    ingredients: List[RecipeIngredient]
    steps: List[RecipeStep]
    
    # Tags và mô tả
    tags: Optional[List[str]] = None  # ["lành mạnh", "truyền thống", "nhanh"]
    description: Optional[str] = None
    image_url: Optional[str] = None


class RecipeSuggestionRequest(BaseModel):
    """Request đề xuất công thức"""
    available_ingredients: Optional[List[str]] = None  # Nguyên liệu có sẵn
    dietary_restrictions: Optional[List[str]] = None  # Hạn chế dinh dưỡng
    max_calories: Optional[float] = None
    region_preference: Optional[str] = None  # "Bắc", "Trung", "Nam"
    meal_type: Optional[str] = None  # "sáng", "trưa", "tối"
    cuisine_style: Optional[str] = None  # "truyền thống", "hiện đại", "lành mạnh"


class RecipeSuggestionResponse(BaseModel):
    """Response đề xuất công thức"""
    recipes: List[Recipe]
    matched_ingredients: Dict[str, List[str]]  # Món nào khớp với nguyên liệu nào
    suggestion_reason: str  # Lý do đề xuất

