"""
Tool: Generate recipe - Tạo công thức món ăn Việt Nam
"""
try:
    from langchain_core.tools import BaseTool
except ImportError:
    from langchain.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from app.config import settings
from app.database.postgres import SessionLocal
from app.database.models import Recipe
import json


class RecipeGeneratorToolInput(BaseModel):
    ingredients: str = Field(description="Danh sách nguyên liệu có sẵn (VD: 'thịt heo, trứng, rau muống')")
    dietary_restrictions: Optional[str] = Field(default="", description="Hạn chế dinh dưỡng (VD: 'tiểu đường, không cay')")
    region_preference: Optional[str] = Field(default=None, description="Vùng miền ưu tiên: Bắc, Trung, Nam")
    meal_type: Optional[str] = Field(default=None, description="Loại bữa: sáng, trưa, tối")
    max_calories: Optional[float] = Field(default=None, description="Giới hạn calo mỗi phần")


class RecipeGeneratorTool(BaseTool):
    """
    Tool tạo công thức món ăn Việt Nam dựa trên nguyên liệu có sẵn
    Tập trung vào các món ăn truyền thống và hiện đại của Việt Nam
    """
    name: str = "recipe_generator_tool"
    description: str = """
    Tạo công thức món ăn Việt Nam dựa trên nguyên liệu có sẵn và yêu cầu dinh dưỡng.
    Gợi ý các món ăn Việt phổ biến: canh rau muống thịt bằm, canh chua cá, cơm rang, etc.
    Trả về công thức chi tiết với nguyên liệu, cách làm từng bước.
    """
    args_schema: Type[BaseModel] = RecipeGeneratorToolInput
    
    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    
    def _run(
        self,
        ingredients: str,
        dietary_restrictions: str = "",
        region_preference: Optional[str] = None,
        meal_type: Optional[str] = None,
        max_calories: Optional[float] = None
    ) -> str:
        """
        Tạo công thức nấu ăn Việt Nam từ nguyên liệu
        """
        try:
            # Thử tìm công thức trong database trước
            db_recipe = self._search_database_recipes(ingredients, region_preference, meal_type)
            if db_recipe:
                return db_recipe
            
            # Nếu không tìm thấy, sử dụng LLM để generate
            if self.client:
                return self._generate_with_llm(ingredients, dietary_restrictions, region_preference, meal_type, max_calories)
            else:
                return self._generate_basic_recipe(ingredients)
                
        except Exception as e:
            return f"Lỗi khi tạo công thức: {str(e)}"
    
    def _search_database_recipes(self, ingredients: str, region: Optional[str], meal_type: Optional[str]) -> Optional[str]:
        """Tìm công thức trong database"""
        try:
            db = SessionLocal()
            query = db.query(Recipe)
            
            if region:
                query = query.filter(Recipe.region == region)
            
            recipes = query.limit(3).all()
            db.close()
            
            if recipes:
                results = []
                for recipe in recipes:
                    results.append({
                        "name": recipe.name_vn,
                        "category": recipe.category,
                        "region": recipe.region,
                        "cooking_time_minutes": recipe.cooking_time_minutes,
                        "calories_per_serving": recipe.calories_per_serving
                    })
                return json.dumps(results, ensure_ascii=False, indent=2)
            return None
        except:
            return None
    
    def _generate_with_llm(
        self,
        ingredients: str,
        dietary_restrictions: str,
        region_preference: Optional[str],
        meal_type: Optional[str],
        max_calories: Optional[float]
    ) -> str:
        """Generate công thức với LLM"""
        prompt = f"""
        Bạn là chuyên gia ẩm thực Việt Nam. Hãy tạo công thức món ăn Việt Nam dựa trên nguyên liệu có sẵn.
        
        Nguyên liệu có sẵn: {ingredients}
        Hạn chế dinh dưỡng: {dietary_restrictions if dietary_restrictions else 'Không có'}
        Vùng miền ưu tiên: {region_preference if region_preference else 'Không yêu cầu'}
        Loại bữa: {meal_type if meal_type else 'Không yêu cầu'}
        Giới hạn calo: {max_calories if max_calories else 'Không giới hạn'}
        
        Trả về JSON với format:
        {{
            "recipe_name": "Tên món ăn tiếng Việt",
            "recipe_name_en": "Tên tiếng Anh",
            "category": "canh/cơm/bún/etc",
            "region": "Bắc/Trung/Nam",
            "difficulty": "Dễ/Trung bình/Khó",
            "cooking_time_minutes": số phút,
            "servings": số phần,
            "calories_per_serving": calo mỗi phần,
            "ingredients": [
                {{"name": "tên", "quantity": số, "unit": "đơn vị", "preparation": "chuẩn bị"}}
            ],
            "steps": [
                {{"step_number": 1, "instruction": "hướng dẫn", "duration_minutes": số phút}}
            ],
            "tips": "Mẹo nấu ăn",
            "nutrition_note": "Ghi chú dinh dưỡng"
        }}
        
        Tập trung vào các món ăn Việt Nam phổ biến, dễ nấu, phù hợp với nguyên liệu.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia ẩm thực Việt Nam với kiến thức sâu về các món ăn truyền thống và hiện đại."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def _generate_basic_recipe(self, ingredients: str) -> str:
        """Generate công thức cơ bản (fallback)"""
        return json.dumps({
            "recipe_name": f"Món ăn từ {ingredients}",
            "message": "Cần cấu hình OpenAI API key để generate công thức chi tiết",
            "ingredients": ingredients.split(","),
            "steps": ["Công thức chi tiết cần được tạo bằng LLM"]
        }, ensure_ascii=False, indent=2)

