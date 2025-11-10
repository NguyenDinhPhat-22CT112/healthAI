"""
Tool: Query DB - Truy vấn thông tin dinh dưỡng và rules bệnh lý
"""
try:
    from langchain_core.tools import BaseTool
except ImportError:
    from langchain.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.postgres import SessionLocal
from app.database.models import Food, DiseaseRule, Recipe
import json


class DBQueryToolInput(BaseModel):
    query_type: str = Field(description="Loại query: 'food_info', 'disease_rules', 'recipe_search', 'nutrition_estimate'")
    food_name: Optional[str] = Field(default=None, description="Tên món ăn cần tìm")
    disease_name: Optional[str] = Field(default=None, description="Tên bệnh lý")
    category: Optional[str] = Field(default=None, description="Nhóm món: phở, bún, cơm, etc.")
    region: Optional[str] = Field(default=None, description="Vùng miền: Bắc, Trung, Nam")


class DBQueryTool(BaseTool):
    """
    Tool truy vấn database để lấy thông tin dinh dưỡng, rules bệnh lý, và công thức món ăn Việt Nam
    """
    name: str = "db_query_tool"
    description: str = """
    Truy vấn PostgreSQL để lấy:
    - Thông tin dinh dưỡng của món ăn Việt Nam (calo, protein, carbs, fat)
    - Rules dinh dưỡng cho bệnh lý phổ biến tại Việt Nam (tiểu đường, mỡ máu, huyết áp cao, gout)
    - Công thức món ăn theo category hoặc region
    """
    args_schema: Type[BaseModel] = DBQueryToolInput
    
    def _run(
        self,
        query_type: str,
        food_name: Optional[str] = None,
        disease_name: Optional[str] = None,
        category: Optional[str] = None,
        region: Optional[str] = None
    ) -> str:
        """
        Thực hiện truy vấn database
        """
        db: Session = SessionLocal()
        try:
            if query_type == "food_info":
                return self._get_food_info(db, food_name, category, region)
            elif query_type == "disease_rules":
                return self._get_disease_rules(db, disease_name)
            elif query_type == "recipe_search":
                return self._search_recipes(db, category, region)
            elif query_type == "nutrition_estimate":
                return self._estimate_nutrition(db, food_name)
            else:
                return f"Loại query không hợp lệ: {query_type}"
        except Exception as e:
            return f"Lỗi truy vấn database: {str(e)}"
        finally:
            db.close()
    
    def _get_food_info(self, db: Session, food_name: Optional[str], category: Optional[str], region: Optional[str]) -> str:
        """Lấy thông tin món ăn"""
        query = db.query(Food)
        
        if food_name:
            query = query.filter(
                Food.name.ilike(f"%{food_name}%")
            )
        
        foods = query.limit(10).all()
        
        if not foods:
            return "Không tìm thấy món ăn phù hợp"
        
        results = []
        for food in foods:
            results.append({
                "name": food.name,
                "calo_per_100g": food.calo,
                "glucid": food.glucid,
                "lipid": food.lipid,
                "protid": food.protid,
                "fiber": food.fiber,
                "vitamins": food.vitamins if food.vitamins else {},
                "tags": food.tags if food.tags else {}
            })
        
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    def _get_disease_rules(self, db: Session, disease_name: Optional[str]) -> str:
        """Lấy rules dinh dưỡng cho bệnh lý"""
        query = db.query(DiseaseRule)
        
        if disease_name:
            query = query.filter(
                or_(
                    DiseaseRule.disease_name.ilike(f"%{disease_name}%"),
                    DiseaseRule.disease_name_en.ilike(f"%{disease_name}%")
                )
            )
        
        rules = query.all()
        
        if not rules:
            return "Không tìm thấy rules cho bệnh lý này"
        
        results = []
        for rule in rules:
            results.append({
                "disease_name": rule.disease_name,
                "allowed_foods": rule.allowed_foods,
                "restricted_foods": rule.restricted_foods,
                "max_calories_per_meal": rule.max_calories_per_meal,
                "max_carbs_per_meal": rule.max_carbs_per_meal,
                "recommendations": rule.recommendations,
                "vietnamese_specific_advice": rule.vietnamese_specific_advice
            })
        
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    def _search_recipes(self, db: Session, category: Optional[str], region: Optional[str]) -> str:
        """Tìm công thức món ăn"""
        query = db.query(Recipe)
        
        if category:
            query = query.filter(Recipe.category == category)
        if region:
            query = query.filter(Recipe.region == region)
        
        recipes = query.limit(5).all()
        
        if not recipes:
            return "Không tìm thấy công thức phù hợp"
        
        results = []
        for recipe in recipes:
            results.append({
                "name": recipe.name_vn,
                "category": recipe.category,
                "region": recipe.region,
                "difficulty": recipe.difficulty,
                "cooking_time_minutes": recipe.cooking_time_minutes,
                "calories_per_serving": recipe.calories_per_serving
            })
        
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    def _estimate_nutrition(self, db: Session, food_name: Optional[str]) -> str:
        """Ước tính dinh dưỡng cho món ăn"""
        if not food_name:
            return "Cần cung cấp tên món ăn"
        
        food = db.query(Food).filter(
            Food.name.ilike(f"%{food_name}%")
        ).first()
        
        if not food:
            return f"Không tìm thấy thông tin dinh dưỡng cho '{food_name}'"
        
        serving_g = 300  # Default 300g nếu không có typical_serving
        
        result = {
            "food_name": food.name,
            "estimated_serving_g": serving_g,
            "nutrition_per_100g": {
                "calo": food.calo,
                "protid": food.protid,
                "lipid": food.lipid,
                "glucid": food.glucid,
                "fiber": food.fiber
            },
            "nutrition_per_serving": {
                "calo": round((food.calo * serving_g) / 100, 2) if food.calo else None,
                "protid": round((food.protid * serving_g) / 100, 2) if food.protid else None,
                "lipid": round((food.lipid * serving_g) / 100, 2) if food.lipid else None,
                "glucid": round((food.glucid * serving_g) / 100, 2) if food.glucid else None,
                "fiber": round((food.fiber * serving_g) / 100, 2) if food.fiber else None
            },
            "vitamins": food.vitamins if food.vitamins else {}
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)

