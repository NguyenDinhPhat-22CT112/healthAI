"""
API: Tính calo và dinh dưỡng - Món ăn Việt Nam
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.postgres import get_db
from app.database.models import FoodItem
from app.tools.db_query_tool import DBQueryTool
import json

router = APIRouter(prefix="/calculate-calories", tags=["Calories"])


class FoodInput(BaseModel):
    """Input cho món ăn"""
    name: str  # Tên món ăn (VD: "Phở bò", "Cơm tấm")
    quantity: float  # Số lượng (gram hoặc khẩu phần)
    unit: Optional[str] = "g"  # Đơn vị: "g" (gram) hoặc "serving" (khẩu phần)


class CalculateCaloriesRequest(BaseModel):
    """Request tính calo"""
    foods: List[FoodInput]
    user_id: Optional[str] = None


class NutritionSummary(BaseModel):
    """Tổng hợp dinh dưỡng"""
    total_calories: float
    total_protein: Optional[float] = None
    total_fat: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fiber: Optional[float] = None
    food_details: List[dict]


@router.post("/", response_model=dict)
async def calculate_calories(
    request: CalculateCaloriesRequest,
    db: Session = Depends(get_db)
):
    """
    Tính tổng calo và dinh dưỡng từ danh sách món ăn Việt Nam
    
    Ví dụ:
    - Phở bò: 1 tô (300g) ~ 450 calories
    - Cơm tấm sườn nướng: 1 phần (350g) ~ 650 calories
    - Gỏi cuốn: 3 cuốn (150g) ~ 180 calories
    """
    db_query_tool = DBQueryTool()
    
    total_calories = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_carbs = 0.0
    total_fiber = 0.0
    
    food_details = []
    
    for food_input in request.foods:
        # Tìm món ăn trong database
        food = db.query(FoodItem).filter(
            FoodItem.name.ilike(f"%{food_input.name}%")
        ).first()
        
        if food:
            # Tính dinh dưỡng dựa trên quantity
            if food_input.unit == "serving":
                # Sử dụng khẩu phần điển hình (default 300g)
                serving_g = 300
                actual_weight = serving_g * food_input.quantity
            else:
                # Sử dụng gram
                actual_weight = food_input.quantity
            
            # Tính toán dinh dưỡng (per 100g)
            calo = (food.calories * actual_weight) / 100 if food.calories else 0
            protid = (food.protein * actual_weight) / 100 if food.protein else 0
            lipid = (food.fat * actual_weight) / 100 if food.fat else 0
            glucid = (food.carbs * actual_weight) / 100 if food.carbs else 0
            fiber = (food.fiber * actual_weight) / 100 if food.fiber else 0
            
            total_calories += calo
            total_protein += protid
            total_fat += lipid
            total_carbs += glucid
            total_fiber += fiber
            
            food_details.append({
                "food_name": food.name,
                "quantity": food_input.quantity,
                "unit": food_input.unit,
                "actual_weight_g": actual_weight,
                "calo": round(calo, 2),
                "protid": round(protid, 2),
                "lipid": round(lipid, 2),
                "glucid": round(glucid, 2),
                "fiber": round(fiber, 2)
            })
        else:
            # Không tìm thấy trong database, thử query với tool
            nutrition_result = db_query_tool._run(
                query_type="nutrition_estimate",
                food_name=food_input.name
            )
            
            try:
                nutrition_data = json.loads(nutrition_result)
                if isinstance(nutrition_data, dict) and "nutrition_per_serving" in nutrition_data:
                    nut = nutrition_data["nutrition_per_serving"]
                    calories = nut.get("calories", 0) * food_input.quantity
                    total_calories += calories
                    
                    food_details.append({
                        "food_name": food_input.name,
                        "quantity": food_input.quantity,
                        "unit": food_input.unit,
                        "calories": round(calories, 2),
                        "nutrition_source": "estimated"
                    })
            except:
                food_details.append({
                    "food_name": food_input.name,
                    "quantity": food_input.quantity,
                    "unit": food_input.unit,
                    "error": "Không tìm thấy thông tin dinh dưỡng"
                })
    
    # Tính toán khuyến nghị (dựa trên người Việt trung bình)
    daily_calorie_needs = 2000  # Default cho người Việt trung bình
    percentage_of_daily = (total_calories / daily_calorie_needs) * 100
    
    result = {
        "status": "success",
        "summary": {
            "total_calories": round(total_calories, 2),
            "total_protein": round(total_protein, 2),
            "total_fat": round(total_fat, 2),
            "total_carbs": round(total_carbs, 2),
            "total_fiber": round(total_fiber, 2),
            "percentage_of_daily_needs": round(percentage_of_daily, 2)
        },
        "food_details": food_details,
        "recommendations": []
    }
    
    # Thêm khuyến nghị
    if total_calories > daily_calorie_needs * 0.5:
        result["recommendations"].append("Bữa ăn này chiếm hơn 50% nhu cầu calo hàng ngày. Bạn nên điều chỉnh các bữa ăn khác.")
    
    if total_fat > 50:
        result["recommendations"].append("Hàm lượng chất béo khá cao. Nên giảm lượng dầu mỡ trong các món ăn.")
    
    if total_protein < 20:
        result["recommendations"].append("Bữa ăn cần bổ sung thêm protein từ thịt, cá, đậu.")
    
    return result

