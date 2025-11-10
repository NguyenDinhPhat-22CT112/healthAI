"""
API: Tư vấn bữa ăn từ ảnh - Món ăn Việt Nam
"""
import os
import base64
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
from app.tools.vision_tool import VisionTool
from app.tools.db_query_tool import DBQueryTool
from app.tools.recipe_generator_tool import RecipeGeneratorTool
from app.agents.food_advisor_agent import FoodAdvisorAgent
from app.models.food import FoodNutritionResponse
from app.models.disease import HealthAdviceRequest, HealthAdviceResponse
from app.database.mongo import get_mongo_db
from datetime import datetime
import json

router = APIRouter(prefix="/analyze-meal", tags=["Meal Analysis"])


class AnalyzeMealRequest(BaseModel):
    """Request cho phân tích bữa ăn"""
    user_id: Optional[str] = None
    diseases: Optional[list] = None  # Danh sách bệnh lý
    region: Optional[str] = None  # Vùng miền người dùng
    include_health_advice: bool = True  # Có bao gồm lời khuyên sức khỏe không


@router.post("/")
async def analyze_meal(
    image: UploadFile = File(...),
    user_id: Optional[str] = None,
    diseases: Optional[str] = None,
    region: Optional[str] = None
):
    """
    Nhận ảnh bữa ăn Việt Nam và trả về:
    - Nhận diện món ăn và thành phần
    - Tính toán dinh dưỡng (calo, protein, carbs, fat)
    - Lời khuyên dinh dưỡng phù hợp với bệnh lý người Việt
    
    Ví dụ món ăn: Phở bò, Cơm tấm sườn nướng, Gỏi cuốn, Bún bò Huế, etc.
    """
    try:
        # Lưu ảnh tạm thời
        temp_image_path = f"temp_{datetime.now().timestamp()}_{image.filename}"
        with open(temp_image_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        # Khởi tạo tools và agent
        vision_tool = VisionTool()
        db_query_tool = DBQueryTool()
        recipe_tool = RecipeGeneratorTool()
        
        tools = [vision_tool, db_query_tool, recipe_tool]
        agent = FoodAdvisorAgent(tools=tools)
        
        # Phân tích ảnh với vision tool
        vision_result = vision_tool._run(temp_image_path, is_base64=False)
        
        # Parse kết quả vision
        try:
            vision_data = json.loads(vision_result)
            dish_name = vision_data.get("dish_name", "Món ăn Việt Nam")
            main_ingredients = vision_data.get("main_ingredients", [])
            estimated_weight_g = vision_data.get("estimated_weight_g", 300)
        except:
            vision_data = {"dish_name": vision_result}
            dish_name = "Món ăn Việt Nam"
            main_ingredients = []
            estimated_weight_g = 300
        
        # Query dinh dưỡng từ database
        nutrition_result = db_query_tool._run(
            query_type="nutrition_estimate",
            food_name=dish_name
        )
        
        # Phân tích với agent nếu cần lời khuyên
        user_profile = None
        health_advice = None
        
        if user_id or diseases or region:
            user_profile = {
                "diseases": json.loads(diseases) if diseases else [],
                "region": region
            }
            
            # Query disease rules nếu có
            if user_profile["diseases"]:
                disease_rules_result = db_query_tool._run(
                    query_type="disease_rules",
                    disease_name=user_profile["diseases"][0] if user_profile["diseases"] else None
                )
                
                # Tạo lời khuyên với agent
                query = f"Dựa trên món ăn '{dish_name}' và bệnh lý '{', '.join(user_profile['diseases'])}', đưa ra lời khuyên dinh dưỡng phù hợp cho người Việt."
                health_advice = agent.run(query, user_profile)
        
        # Lưu kết quả vào MongoDB (optional)
        mongo_db = get_mongo_db()
        meal_log = {
            "user_id": user_id,
            "timestamp": datetime.now(),
            "image_filename": image.filename,
            "dish_name": dish_name,
            "main_ingredients": main_ingredients,
            "estimated_weight_g": estimated_weight_g,
            "nutrition_data": nutrition_result,
            "health_advice": health_advice,
            "region": region
        }
        mongo_db.meal_logs.insert_one(meal_log)
        
        # Xóa ảnh tạm
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        # Trả về kết quả
        return JSONResponse({
            "status": "success",
            "dish_name": dish_name,
            "main_ingredients": main_ingredients,
            "estimated_weight_g": estimated_weight_g,
            "nutrition": json.loads(nutrition_result) if isinstance(nutrition_result, str) else nutrition_result,
            "health_advice": health_advice,
            "vision_analysis": vision_data
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Lỗi khi phân tích bữa ăn: {str(e)}"}
        )

