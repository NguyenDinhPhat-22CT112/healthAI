"""
Recipe Suggester Service - Gợi ý công thức nấu ăn
"""
from typing import List, Dict, Any
from openai import OpenAI
from app.config import settings


class RecipeSuggesterService:
    """Service gợi ý công thức với AI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    
    async def suggest_recipes(
        self,
        ingredients: List[str],
        preferences: Dict[str, Any] = {},
        user_diseases: List[str] = [],
        dietary_restrictions: List[str] = [],
        allergies: List[str] = []
    ) -> Dict[str, Any]:
        """
        Gợi ý công thức từ nguyên liệu
        
        Returns:
            - recipes: Danh sách công thức
            - health_adapted: Đã điều chỉnh cho bệnh lý chưa
            - health_notes: Ghi chú về điều chỉnh
            - ai_response: Full AI response
        """
        
        if not self.client:
            return self._mock_recipes(ingredients)
        
        try:
            # Build prompt
            system_prompt = self._build_system_prompt(
                user_diseases, dietary_restrictions, allergies
            )
            
            user_prompt = self._build_user_prompt(ingredients, preferences)
            
            # Call GPT
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse response
            result = self._parse_recipes(ai_response, user_diseases)
            result['ai_response'] = ai_response
            
            return result
            
        except Exception as e:
            print(f"Error suggesting recipes: {e}")
            return self._mock_recipes(ingredients)
    
    def _build_system_prompt(
        self,
        diseases: List[str],
        restrictions: List[str],
        allergies: List[str]
    ) -> str:
        """Build system prompt"""
        
        prompt = """Bạn là chuyên gia ẩm thực Việt Nam.

Nhiệm vụ: Gợi ý công thức nấu ăn từ nguyên liệu có sẵn.

Trả lời theo format JSON:
{
  "recipes": [
    {
      "name": "Tên món",
      "ingredients": ["nguyên liệu 1", "nguyên liệu 2"],
      "instructions": ["Bước 1", "Bước 2"],
      "prep_time": 15,
      "cook_time": 30,
      "servings": 2,
      "calories_per_serving": 450,
      "health_notes": "Ghi chú dinh dưỡng"
    }
  ],
  "health_adapted": true,
  "health_notes": "Đã điều chỉnh..."
}

Ưu tiên món ăn Việt Nam. Đưa ra 2-3 công thức."""
        
        if diseases:
            prompt += f"\n\nBệnh lý: {', '.join(diseases)}"
            prompt += "\nĐiều chỉnh công thức phù hợp với bệnh lý."
        
        if allergies:
            prompt += f"\n\nDị ứng: {', '.join(allergies)}"
            prompt += "\nTránh các thành phần gây dị ứng."
        
        if restrictions:
            prompt += f"\n\nHạn chế: {', '.join(restrictions)}"
        
        return prompt
    
    def _build_user_prompt(
        self,
        ingredients: List[str],
        preferences: Dict[str, Any]
    ) -> str:
        """Build user prompt"""
        
        prompt = f"Nguyên liệu có sẵn: {', '.join(ingredients)}\n\n"
        
        if preferences.get('region'):
            prompt += f"Vùng miền ưu tiên: {preferences['region']}\n"
        
        if preferences.get('meal_type'):
            prompt += f"Loại bữa: {preferences['meal_type']}\n"
        
        if preferences.get('cooking_time'):
            prompt += f"Thời gian nấu tối đa: {preferences['cooking_time']} phút\n"
        
        prompt += "\nGợi ý công thức món ăn Việt Nam phù hợp."
        
        return prompt
    
    def _parse_recipes(self, response: str, diseases: List[str]) -> Dict[str, Any]:
        """Parse AI response"""
        
        import json
        import re
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data
        except:
            pass
        
        # Fallback
        return {
            "recipes": [
                {
                    "name": "Món ăn gợi ý",
                    "ingredients": ["Từ nguyên liệu có sẵn"],
                    "instructions": ["Xem chi tiết trong AI response"],
                    "prep_time": 15,
                    "cook_time": 30,
                    "servings": 2,
                    "calories_per_serving": 400
                }
            ],
            "health_adapted": len(diseases) > 0,
            "health_notes": response[:200]
        }
    
    def _mock_recipes(self, ingredients: List[str]) -> Dict[str, Any]:
        """Mock recipes"""
        
        return {
            "recipes": [
                {
                    "name": "Cơm chiên",
                    "ingredients": ingredients + ["cơm nguội", "trứng", "hành"],
                    "instructions": [
                        "Đập trứng, đánh tan",
                        "Phi hành thơm",
                        "Cho cơm vào xào",
                        "Đổ trứng vào trộn đều",
                        "Nêm nếm vừa ăn"
                    ],
                    "prep_time": 10,
                    "cook_time": 15,
                    "servings": 2,
                    "calories_per_serving": 450,
                    "health_notes": "Món ăn nhanh, đơn giản"
                },
                {
                    "name": "Canh rau",
                    "ingredients": ingredients + ["rau", "nước dùng"],
                    "instructions": [
                        "Đun sôi nước",
                        "Cho rau vào",
                        "Nêm nếm",
                        "Tắt bếp"
                    ],
                    "prep_time": 5,
                    "cook_time": 10,
                    "servings": 2,
                    "calories_per_serving": 50,
                    "health_notes": "Ít calo, nhiều chất xơ"
                }
            ],
            "health_adapted": False,
            "health_notes": "Mock recipes - OpenAI API not configured",
            "ai_response": "Mock response"
        }
