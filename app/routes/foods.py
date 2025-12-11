"""
Food API Routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.services.food_service import food_service

router = APIRouter(prefix="/api/foods", tags=["foods"])


class FoodResponse(BaseModel):
    food_id: int
    name: str
    description: Optional[str]
    region: Optional[str]
    category: Optional[str]
    calories: float
    protein: float
    carbs: float
    fat: float


class AnalysisResponse(BaseModel):
    food: dict
    ingredients: List[dict]
    nutrition_score: int
    health_classification: str
    macros: dict
    micronutrients: dict


@router.get("/", response_model=List[FoodResponse])
async def get_foods(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Get all foods with pagination"""
    try:
        foods = food_service.get_all_foods(limit=limit, offset=offset)
        return foods
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{food_id}")
async def get_food(food_id: int):
    """Get food by ID"""
    try:
        food = food_service.get_food_by_id(food_id)
        if not food:
            raise HTTPException(status_code=404, detail="Food not found")
        return food
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/query")
async def search_foods(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Search foods by name or description"""
    try:
        foods = food_service.search_foods(query=q, limit=limit)
        return {"query": q, "results": foods, "count": len(foods)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/{food_id}", response_model=AnalysisResponse)
async def analyze_food(food_id: int):
    """Analyze food nutrition"""
    try:
        analysis = food_service.analyze_food_nutrition(food_id)
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/{condition}")
async def get_foods_for_condition(condition: str):
    """Get recommended foods for health condition"""
    try:
        foods = food_service.get_foods_by_health_condition(condition)
        return {
            "condition": condition,
            "recommended_foods": foods,
            "count": len(foods)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{food_id}/ingredients")
async def get_food_ingredients(food_id: int):
    """Get ingredients for a food"""
    try:
        ingredients = food_service.get_food_ingredients(food_id)
        return {
            "food_id": food_id,
            "ingredients": ingredients,
            "count": len(ingredients)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
