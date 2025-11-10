"""
API: Đề xuất công thức món ăn Việt Nam
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from app.database.postgres import get_db
from app.tools.recipe_generator_tool import RecipeGeneratorTool
from app.tools.db_query_tool import DBQueryTool
from app.tools.vision_tool import VisionTool
from app.agents.food_advisor_agent import FoodAdvisorAgent
from app.models.recipe import RecipeSuggestionRequest, RecipeSuggestionResponse
import json

router = APIRouter(prefix="/suggest-recipe", tags=["Recipe"])


class SuggestRecipeRequest(BaseModel):
    """Request đề xuất công thức"""
    available_ingredients: Optional[List[str]] = None  # VD: ["thịt heo", "trứng", "rau muống"]
    dietary_restrictions: Optional[List[str]] = None  # VD: ["tiểu đường", "không cay"]
    max_calories: Optional[float] = None
    region_preference: Optional[str] = None  # "Bắc", "Trung", "Nam"
    meal_type: Optional[str] = None  # "sáng", "trưa", "tối"
    cuisine_style: Optional[str] = None  # "truyền thống", "hiện đại", "lành mạnh"
    number_of_recipes: Optional[int] = 3  # Số công thức đề xuất


@router.post("/")
async def suggest_recipe(
    request: SuggestRecipeRequest,
    db: Session = Depends(get_db)
):
    """
    Đề xuất công thức món ăn Việt Nam dựa trên:
    - Nguyên liệu có sẵn
    - Hạn chế dinh dưỡng
    - Sở thích vùng miền (Bắc, Trung, Nam)
    - Loại bữa ăn (sáng, trưa, tối)
    
    Ví dụ:
    - Nguyên liệu: "thịt heo, trứng, rau muống" → Gợi ý: "Canh rau muống thịt bằm"
    - Vùng miền: "Nam" → Gợi ý các món đặc trưng miền Nam
    - Loại bữa: "sáng" → Gợi ý các món ăn sáng Việt Nam
    """
    try:
        # Khởi tạo tools và agent
        recipe_tool = RecipeGeneratorTool()
        db_query_tool = DBQueryTool()
        vision_tool = VisionTool()
        
        tools = [recipe_tool, db_query_tool, vision_tool]
        agent = FoodAdvisorAgent(tools=tools)
        
        recipes = []
        
        # Nếu có nguyên liệu, generate công thức
        if request.available_ingredients:
            ingredients_str = ", ".join(request.available_ingredients)
            dietary_str = ", ".join(request.dietary_restrictions) if request.dietary_restrictions else ""
            
            # Sử dụng agent để suggest
            preferences = {
                "region": request.region_preference,
                "meal_type": request.meal_type,
                "dietary_restrictions": request.dietary_restrictions or []
            }
            
            suggestion_result = agent.suggest_recipe(
                ingredients=request.available_ingredients,
                preferences=preferences
            )
            
            recipes.append({
                "source": "agent",
                "suggestion": suggestion_result.get("recipe_suggestion", ""),
                "ingredients": request.available_ingredients,
                "preferences": preferences
            })
            
            # Sử dụng recipe tool để generate chi tiết
            recipe_json = recipe_tool._run(
                ingredients=ingredients_str,
                dietary_restrictions=dietary_str,
                region_preference=request.region_preference,
                meal_type=request.meal_type,
                max_calories=request.max_calories
            )
            
            try:
                recipe_data = json.loads(recipe_json)
                if isinstance(recipe_data, list):
                    recipes.extend(recipe_data)
                elif isinstance(recipe_data, dict):
                    recipes.append(recipe_data)
            except:
                recipes.append({"recipe_json": recipe_json})
        
        # Tìm công thức trong database theo category/region
        if request.region_preference or request.meal_type:
            category_map = {
                "sáng": "phở",
                "trưa": "cơm",
                "tối": "cơm"
            }
            
            category = category_map.get(request.meal_type) if request.meal_type else None
            
            db_recipes = db_query_tool._run(
                query_type="recipe_search",
                category=category,
                region=request.region_preference
            )
            
            try:
                db_recipes_data = json.loads(db_recipes)
                if isinstance(db_recipes_data, list):
                    recipes.extend(db_recipes_data)
            except:
                pass
        
        # Lọc theo max_calories nếu có
        if request.max_calories:
            filtered_recipes = []
            for recipe in recipes:
                if isinstance(recipe, dict):
                    calories = recipe.get("calories_per_serving", 0)
                    if calories <= request.max_calories:
                        filtered_recipes.append(recipe)
                else:
                    filtered_recipes.append(recipe)
            recipes = filtered_recipes[:request.number_of_recipes]
        
        # Format response
        result = {
            "status": "success",
            "recipes": recipes[:request.number_of_recipes],
            "total_found": len(recipes),
            "criteria": {
                "available_ingredients": request.available_ingredients,
                "dietary_restrictions": request.dietary_restrictions,
                "region_preference": request.region_preference,
                "meal_type": request.meal_type,
                "max_calories": request.max_calories
            },
            "suggestion_note": "Các công thức được đề xuất dựa trên nguyên liệu và sở thích của bạn, phù hợp với ẩm thực Việt Nam."
        }
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi khi đề xuất công thức: {str(e)}"
        }


@router.get("/popular-vietnamese")
async def get_popular_vietnamese_recipes():
    """
    Lấy danh sách các món ăn Việt Nam phổ biến
    """
    popular_recipes = [
        {
            "name": "Phở bò",
            "category": "phở",
            "region": "Bắc",
            "meal_type": "sáng",
            "calories_per_serving": 450,
            "difficulty": "Trung bình"
        },
        {
            "name": "Bún bò Huế",
            "category": "bún",
            "region": "Trung",
            "meal_type": "sáng",
            "calories_per_serving": 550,
            "difficulty": "Khó"
        },
        {
            "name": "Cơm tấm sườn nướng",
            "category": "cơm",
            "region": "Nam",
            "meal_type": "trưa",
            "calories_per_serving": 650,
            "difficulty": "Dễ"
        },
        {
            "name": "Gỏi cuốn",
            "category": "gỏi",
            "region": "Nam",
            "meal_type": "tối",
            "calories_per_serving": 60,
            "difficulty": "Dễ"
        },
        {
            "name": "Bánh xèo",
            "category": "bánh",
            "region": "Nam",
            "meal_type": "tối",
            "calories_per_serving": 350,
            "difficulty": "Trung bình"
        }
    ]
    
    return {
        "status": "success",
        "recipes": popular_recipes,
        "total": len(popular_recipes)
    }

