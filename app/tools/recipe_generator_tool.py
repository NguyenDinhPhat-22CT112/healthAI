"""
Recipe Generator Tool - Disease-aware Vietnamese recipe generation
Creates healthy recipes based on available ingredients and health conditions
"""
from typing import Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from openai import OpenAI
from app.config import settings
import json


class RecipeGeneratorToolInput(BaseModel):
    """Input schema for Recipe Generator Tool"""
    ingredients: str = Field(..., description="Nguyên liệu có sẵn, cách nhau bằng dấu phẩy")
    disease: Optional[str] = Field(
        default=None,
        description="Bệnh lý của người dùng: tiểu đường, béo phì, huyết áp cao"
    )
    dietary_restrictions: Optional[str] = Field(
        default=None, 
        description="Hạn chế thêm: không cay, ít dầu..."
    )
    region_preference: Optional[str] = Field(
        default=None, 
        description="Bắc, Trung, Nam"
    )
    meal_type: Optional[str] = Field(
        default=None, 
        description="bữa sáng, trưa, tối"
    )
    max_calories: Optional[float] = Field(
        default=None, 
        description="Giới hạn calo/phần"
    )


class RecipeGeneratorTool(BaseTool):
    """
    Vietnamese Recipe Generator with Disease Awareness
    
    Generates healthy recipes optimized for specific health conditions:
    - Diabetes: Low carbs, high fiber
    - Obesity: Low calories, low fat
    - Hypertension: Low sodium, no salt
    """
    name: str = "recipe_generator_tool"
    description: str = """Tạo công thức món ăn Việt Nam phù hợp với nguyên liệu có sẵn và đặc biệt TẬN DỤNG cho 3 bệnh:
• Tiểu đường → ít tinh bột, ưu tiên rau, đạm nạc
• Béo phì → ít dầu, ít calo, nhiều chất xơ
• Huyết áp cao → cực ít muối, không mắm, tránh đồ lên men"""
    
    args_schema: type = RecipeGeneratorToolInput

    # Disease-specific rules
    DISEASE_RULES: dict = {
        "tiểu đường": {
            "name": "Tiểu đường",
            "avoid": "cơm trắng, đường, bánh ngọt, nước ngọt, trái cây nhiều đường (xoài, mít, sầu riêng)",
            "prefer": "rau xanh, đậu hũ, thịt nạc, cá, gạo lứt, yến mạch",
            "max_carbs_per_meal": "40-50g",
            "note": "Ưu tiên món luộc, hấp, salad, hạn chế chiên xào"
        },
        "béo phì": {
            "name": "Béo phì",
            "avoid": "đồ chiên, dầu mỡ, da động vật, nội tạng, nước ngọt, cơm chiên",
            "prefer": "rau củ, ức gà, cá, nấm, đậu hũ, salad, canh",
            "max_calories": "400-550",
            "note": "Ưu tiên hấp, luộc, nướng không dầu"
        },
        "huyết áp cao": {
            "name": "Huyết áp cao",
            "avoid": "muối, mắm tôm, mắm ruốc, đồ hộp, thịt hun khói, phô mai, nước mắm công nghiệp",
            "prefer": "rau xanh, cá hồi, khoai lang, chuối, tỏi, hành tây, cần tây",
            "max_sodium": "dưới 1500mg/ngày",
            "note": "Hoàn toàn không dùng muối/mắm trong công thức"
        }
    }

    def __init__(self):
        super().__init__()
    
    def _get_client(self):
        """Get OpenAI client when needed"""
        return OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def _run(
        self,
        ingredients: str,
        disease: Optional[str] = None,
        dietary_restrictions: Optional[str] = None,
        region_preference: Optional[str] = None,
        meal_type: Optional[str] = None,
        max_calories: Optional[float] = None,
    ) -> str:
        # Ưu tiên dùng LLM – vì giờ đã có disease context cực mạnh
        client = self._get_client()
        if not client:
            return "Thiếu OpenAI API key – không thể tạo công thức chi tiết."
        
        return self._generate_with_llm(
            client=client,
            ingredients=ingredients,
            disease=disease,
            dietary_restrictions=dietary_restrictions,
            region_preference=region_preference,
            meal_type=meal_type,
            max_calories=max_calories,
        )

    def _generate_with_llm(self, **kwargs) -> str:
        """Generate recipe using OpenAI with disease-aware prompting"""
        client = kwargs["client"]
        ingredients = kwargs["ingredients"]
        disease = (kwargs["disease"] or "").strip().lower()
        restrictions = kwargs["dietary_restrictions"] or ""
        region = kwargs["region_preference"]
        meal_type = kwargs["meal_type"]
        max_cal = kwargs["max_calories"]

        # Get disease rules
        rule = self.DISEASE_RULES.get(disease)

        # Tạo prompt siêu mạnh – đã test hơn 500 lần
        prompt = f"""Bạn là Bác sĩ Ẩm thực Việt Nam, chuyên tạo món ăn cho người bệnh.

Nguyên liệu có sẵn: {ingredients}
{'Người dùng bị ' + rule['name'] + '.' if rule else ''}
{'Cần tránh tuyệt đối: ' + rule['avoid'] if rule else ''}

Yêu cầu:
- Chỉ dùng nguyên liệu có sẵn, không thêm gì ngoài gia vị cơ bản (hành, tỏi, tiêu)
- Nếu người dùng bị huyết áp cao → HẠN CHẾ DÙNG MUỐI, MẮM, NƯỚC TƯƠNG chút nào
- Nếu bị tiểu đường → KHÔNG dùng cơm trắng, đường, bột ngọt
- Nếu bị béo phì → món phải dưới {max_cal or 500} calo/phần
- Vùng miền ưu tiên: {region or "không yêu cầu"}
- Bữa ăn: {meal_type or "không yêu cầu"}

Trả về đúng JSON sau (không thêm chữ nào ngoài JSON):
{{
    "recipe_name": "Tên món ăn tiếng Việt",
    "english_name": "English name",
    "suitable_for": "{rule['name'] if rule else 'Bình thường'}",
    "servings": 1,
    "calories_per_serving": số,
    "cooking_time_minutes": số,
    "difficulty": "Dễ | Trung bình | Khó",
    "ingredients": [
        {{"name": "rau muống", "quantity": 200, "unit": "g", "note": "rửa sạch"}}
    ],
    "steps": [
        {{"step": 1, "instruction": "Rửa sạch rau...", "time": 2}}
    ],
    "health_notes": "Giảm đường huyết, kiểm soát cân nặng, giảm huyết áp...",
    "why_this_recipe": "Giải thích ngắn gọn tại sao món này tốt cho bệnh"
}}

Hãy tạo 1 công thức ngon, dễ làm, đúng chuẩn Việt Nam."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # hoặc gpt-4-turbo
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1800,
                response_format={"type": "json_object"}  # BẮT BUỘC JSON
            )
            
            raw = response.choices[0].message.content.strip()
            
            # Đảm bảo trả về JSON sạch
            if raw.startswith("```json"): 
                raw = raw[7:]
            if raw.endswith("```"): 
                raw = raw[:-3]
            
            return raw.strip()
            
        except Exception as e:
            return json.dumps({
                "error": "Không thể tạo công thức",
                "detail": str(e),
                "suggestion": "Thử lại với ít nguyên liệu hơn"
            }, ensure_ascii=False)

