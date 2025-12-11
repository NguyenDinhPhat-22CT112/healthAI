"""
Recipe Routes - Gợi ý công thức nấu ăn
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.database.models import User, HealthProfile, Recipe
from app.schemas.meal import RecipeQueryRequest, RecipeQueryResponse
from app.auth.dependencies import get_current_active_user
from app.services.recipe_suggester import RecipeSuggesterService

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.post("/suggest", response_model=RecipeQueryResponse)
async def suggest_recipes(
    request: RecipeQueryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Gợi ý công thức nấu ăn từ nguyên liệu
    
    - Nhận danh sách nguyên liệu có sẵn
    - Tự động điều chỉnh công thức phù hợp với bệnh lý
    - Đưa ra lời khuyên dinh dưỡng
    """
    
    if not request.ingredients:
        raise HTTPException(status_code=400, detail="Ingredients list cannot be empty")
    
    # Get user's health profile
    health_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    # Get recipe suggestions with AI
    suggester = RecipeSuggesterService()
    result = await suggester.suggest_recipes(
        ingredients=request.ingredients,
        preferences=request.preferences,
        user_diseases=health_profile.diseases if health_profile else [],
        dietary_restrictions=health_profile.dietary_restrictions if health_profile else [],
        allergies=health_profile.allergies if health_profile else []
    )
    
    # Save to database
    recipe_query = RecipeQuery(
        user_id=current_user.id,
        ingredients=request.ingredients,
        preferences=request.preferences,
        suggested_recipes=result['recipes'],
        health_adapted=result['health_adapted'],
        health_notes=result['health_notes'],
        ai_response=result['ai_response']
    )
    
    db.add(recipe_query)
    db.commit()
    db.refresh(recipe_query)
    
    return recipe_query


@router.get("/history", response_model=List[RecipeQueryResponse])
def get_recipe_history(
    limit: int = 20,
    skip: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lấy lịch sử gợi ý công thức"""
    
    recipes = db.query(RecipeQuery).filter(
        RecipeQuery.user_id == current_user.id
    ).order_by(RecipeQuery.created_at.desc()).offset(skip).limit(limit).all()
    
    return recipes


@router.get("/{query_id}", response_model=RecipeQueryResponse)
def get_recipe_query(
    query_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết một gợi ý công thức"""
    
    recipe = db.query(RecipeQuery).filter(
        RecipeQuery.id == query_id,
        RecipeQuery.user_id == current_user.id
    ).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe query not found")
    
    return recipe


@router.delete("/{query_id}")
def delete_recipe_query(
    query_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Xóa một gợi ý công thức"""
    
    recipe = db.query(RecipeQuery).filter(
        RecipeQuery.id == query_id,
        RecipeQuery.user_id == current_user.id
    ).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe query not found")
    
    db.delete(recipe)
    db.commit()
    
    return {"message": "Recipe query deleted successfully"}


@router.get("/popular/vietnamese")
def get_popular_vietnamese_recipes():
    """Lấy danh sách món ăn Việt Nam phổ biến"""
    
    popular_recipes = [
        {
            "name": "Phở bò",
            "category": "Bún/Phở",
            "region": "Bắc",
            "calories": 450,
            "description": "Món ăn truyền thống Việt Nam với nước dùng thơm ngon"
        },
        {
            "name": "Cơm tấm sườn nướng",
            "category": "Cơm",
            "region": "Nam",
            "calories": 650,
            "description": "Cơm tấm với sườn nướng, trứng ốp la"
        },
        {
            "name": "Bún bò Huế",
            "category": "Bún/Phở",
            "region": "Trung",
            "calories": 550,
            "description": "Món bún cay nồng đặc trưng miền Trung"
        },
        {
            "name": "Gỏi cuốn",
            "category": "Khai vị",
            "region": "Nam",
            "calories": 60,
            "description": "Món ăn nhẹ, tươi mát với rau và tôm thịt"
        },
        {
            "name": "Bánh xèo",
            "category": "Bánh",
            "region": "Nam",
            "calories": 350,
            "description": "Bánh giòn với nhân tôm thịt và giá đỗ"
        }
    ]
    
    return {
        "recipes": popular_recipes,
        "total": len(popular_recipes)
    }
