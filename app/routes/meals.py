"""
Meal Analysis Routes - Phân tích bữa ăn từ ảnh
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime

from app.database.connection import get_db
from app.database.models import User, HealthProfile, ImageAnalysis
from app.schemas.meal import MealAnalysisResponse
from app.auth.dependencies import get_current_active_user
from app.services.meal_analyzer import MealAnalyzerService

router = APIRouter(prefix="/meals", tags=["Meal Analysis"])


@router.post("/analyze", response_model=MealAnalysisResponse)
async def analyze_meal(
    image: UploadFile = File(...),
    meal_type: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Phân tích bữa ăn từ ảnh
    
    - Nhận diện món ăn trong ảnh
    - Tính toán calo và dinh dưỡng
    - Đánh giá phù hợp với bệnh lý của user
    - Đưa ra lời khuyên cụ thể
    """
    
    # Validate image
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save image
    upload_dir = "uploads/meals"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ext = os.path.splitext(image.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as f:
        content = await image.read()
        f.write(content)
    
    # Get user's health profile
    health_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    # Analyze meal with AI
    analyzer = MealAnalyzerService()
    analysis_result = await analyzer.analyze_meal_image(
        image_path=file_path,
        user_diseases=health_profile.diseases if health_profile else [],
        user_allergies=health_profile.allergies if health_profile else [],
        dietary_restrictions=health_profile.dietary_restrictions if health_profile else []
    )
    
    # Save to database
    meal_analysis = MealAnalysis(
        user_id=current_user.id,
        image_path=file_path,
        detected_foods=analysis_result['detected_foods'],
        total_calories=analysis_result['total_calories'],
        total_protein=analysis_result['total_protein'],
        total_carbs=analysis_result['total_carbs'],
        total_fat=analysis_result['total_fat'],
        health_assessment=analysis_result['health_assessment'],
        recommendations=analysis_result['recommendations'],
        warnings=analysis_result['warnings'],
        suitability_score=analysis_result['suitability_score'],
        ai_analysis=analysis_result['ai_analysis'],
        meal_type=meal_type,
        meal_time=datetime.utcnow()
    )
    
    db.add(meal_analysis)
    db.commit()
    db.refresh(meal_analysis)
    
    return meal_analysis


@router.get("/history", response_model=list[MealAnalysisResponse])
def get_meal_history(
    limit: int = 20,
    skip: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lấy lịch sử phân tích bữa ăn"""
    
    meals = db.query(MealAnalysis).filter(
        MealAnalysis.user_id == current_user.id
    ).order_by(MealAnalysis.created_at.desc()).offset(skip).limit(limit).all()
    
    return meals


@router.get("/{meal_id}", response_model=MealAnalysisResponse)
def get_meal_analysis(
    meal_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết một phân tích bữa ăn"""
    
    meal = db.query(MealAnalysis).filter(
        MealAnalysis.id == meal_id,
        MealAnalysis.user_id == current_user.id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal analysis not found")
    
    return meal


@router.delete("/{meal_id}")
def delete_meal_analysis(
    meal_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Xóa một phân tích bữa ăn"""
    
    meal = db.query(MealAnalysis).filter(
        MealAnalysis.id == meal_id,
        MealAnalysis.user_id == current_user.id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal analysis not found")
    
    # Delete image file
    if meal.image_path and os.path.exists(meal.image_path):
        os.remove(meal.image_path)
    
    db.delete(meal)
    db.commit()
    
    return {"message": "Meal analysis deleted successfully"}


@router.get("/stats/summary")
def get_meal_stats(
    days: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Thống kê bữa ăn trong N ngày gần đây"""
    
    from datetime import timedelta
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    meals = db.query(MealAnalysis).filter(
        MealAnalysis.user_id == current_user.id,
        MealAnalysis.created_at >= start_date
    ).all()
    
    if not meals:
        return {
            "total_meals": 0,
            "avg_calories": 0,
            "avg_suitability_score": 0,
            "total_warnings": 0
        }
    
    total_calories = sum(m.total_calories for m in meals)
    total_warnings = sum(len(m.warnings) for m in meals)
    avg_suitability = sum(m.suitability_score for m in meals) / len(meals)
    
    return {
        "total_meals": len(meals),
        "avg_calories_per_meal": round(total_calories / len(meals), 2),
        "total_calories": round(total_calories, 2),
        "avg_suitability_score": round(avg_suitability, 2),
        "total_warnings": total_warnings,
        "period_days": days
    }
