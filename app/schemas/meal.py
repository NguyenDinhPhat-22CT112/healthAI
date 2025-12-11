"""
Meal Analysis Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class MealAnalysisRequest(BaseModel):
    """Request phân tích bữa ăn"""
    meal_type: Optional[str] = Field(None, description="breakfast, lunch, dinner, snack")
    meal_time: Optional[datetime] = None
    notes: Optional[str] = None


class DetectedFood(BaseModel):
    """Món ăn được phát hiện"""
    name: str
    confidence: float
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None


class MealAnalysisResponse(BaseModel):
    """Response phân tích bữa ăn"""
    id: str
    detected_foods: List[Dict]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    
    # Đánh giá dựa trên bệnh lý
    health_assessment: str
    recommendations: List[str]
    warnings: List[str]
    suitability_score: float
    
    ai_analysis: str
    meal_type: Optional[str]
    meal_time: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecipeQueryRequest(BaseModel):
    """Request gợi ý công thức"""
    ingredients: List[str] = Field(..., description="Nguyên liệu có sẵn")
    preferences: Optional[Dict] = Field(default_factory=dict, description="Sở thích (region, meal_type, etc.)")


class Recipe(BaseModel):
    """Công thức món ăn"""
    name: str
    ingredients: List[str]
    instructions: List[str]
    prep_time: Optional[int] = None  # minutes
    cook_time: Optional[int] = None  # minutes
    servings: Optional[int] = None
    calories_per_serving: Optional[float] = None
    health_notes: Optional[str] = None


class RecipeQueryResponse(BaseModel):
    """Response gợi ý công thức"""
    id: str
    ingredients: List[str]
    suggested_recipes: List[Dict]
    health_adapted: bool
    health_notes: Optional[str]
    ai_response: str
    created_at: datetime
    
    class Config:
        from_attributes = True
