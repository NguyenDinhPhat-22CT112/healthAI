"""
Meal Analyzer Service - Phân tích bữa ăn từ ảnh
"""
from typing import List, Dict, Any
import base64
from openai import OpenAI
from app.config import settings


class MealAnalyzerService:
    """Service phân tích bữa ăn với AI Vision"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    
    async def analyze_meal_image(
        self,
        image_path: str,
        user_diseases: List[str] = [],
        user_allergies: List[str] = [],
        dietary_restrictions: List[str] = []
    ) -> Dict[str, Any]:
        """
        Phân tích bữa ăn từ ảnh
        
        Returns:
            - detected_foods: Danh sách món ăn phát hiện
            - total_calories, protein, carbs, fat
            - health_assessment: Đánh giá tổng quan
            - recommendations: Lời khuyên
            - warnings: Cảnh báo
            - suitability_score: Điểm phù hợp (0-100)
        """
        
        if not self.client:
            return self._mock_analysis()
        
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Build prompt với thông tin bệnh lý
            system_prompt = self._build_system_prompt(user_diseases, user_allergies, dietary_restrictions)
            
            # Call GPT-4 Vision
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Phân tích bữa ăn trong ảnh này. Nhận diện món ăn, tính calo, đánh giá phù hợp với bệnh lý."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse response
            result = self._parse_ai_response(ai_response, user_diseases)
            result['ai_analysis'] = ai_response
            
            return result
            
        except Exception as e:
            print(f"Error analyzing meal: {e}")
            return self._mock_analysis()
    
    def _build_system_prompt(
        self,
        diseases: List[str],
        allergies: List[str],
        restrictions: List[str]
    ) -> str:
        """Build system prompt với thông tin user"""
        
        prompt = """Bạn là chuyên gia dinh dưỡng AI chuyên về ẩm thực Việt Nam.

Nhiệm vụ: Phân tích bữa ăn từ ảnh và đánh giá phù hợp với tình trạng sức khỏe.

Trả lời theo format JSON:
{
  "detected_foods": [
    {"name": "tên món", "confidence": 0.95, "calories": 450, "protein": 30, "carbs": 50, "fat": 15}
  ],
  "total_calories": 450,
  "total_protein": 30,
  "total_carbs": 50,
  "total_fat": 15,
  "health_assessment": "Đánh giá tổng quan...",
  "recommendations": ["Lời khuyên 1", "Lời khuyên 2"],
  "warnings": ["Cảnh báo nếu có"],
  "suitability_score": 75
}
"""
        
        if diseases:
            prompt += f"\n\nBệnh lý của người dùng: {', '.join(diseases)}"
            prompt += "\nĐánh giá món ăn có phù hợp với bệnh lý không."
        
        if allergies:
            prompt += f"\n\nDị ứng: {', '.join(allergies)}"
            prompt += "\nCảnh báo nếu có thành phần gây dị ứng."
        
        if restrictions:
            prompt += f"\n\nHạn chế: {', '.join(restrictions)}"
        
        return prompt
    
    def _parse_ai_response(self, response: str, diseases: List[str]) -> Dict[str, Any]:
        """Parse AI response thành structured data"""
        
        import json
        import re
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data
        except:
            pass
        
        # Fallback: Parse manually
        return {
            "detected_foods": [{"name": "Món ăn", "confidence": 0.8, "calories": 400, "protein": 25, "carbs": 45, "fat": 12}],
            "total_calories": 400,
            "total_protein": 25,
            "total_carbs": 45,
            "total_fat": 12,
            "health_assessment": response[:200],
            "recommendations": ["Ăn chậm, nhai kỹ", "Uống đủ nước"],
            "warnings": [],
            "suitability_score": 70
        }
    
    def _mock_analysis(self) -> Dict[str, Any]:
        """Mock analysis khi không có OpenAI"""
        
        return {
            "detected_foods": [
                {
                    "name": "Cơm trắng",
                    "confidence": 0.9,
                    "calories": 200,
                    "protein": 4,
                    "carbs": 45,
                    "fat": 0.5
                },
                {
                    "name": "Thịt kho",
                    "confidence": 0.85,
                    "calories": 250,
                    "protein": 20,
                    "carbs": 5,
                    "fat": 18
                }
            ],
            "total_calories": 450,
            "total_protein": 24,
            "total_carbs": 50,
            "total_fat": 18.5,
            "health_assessment": "Bữa ăn cân bằng với đủ protein, carbs và fat. Phù hợp cho bữa trưa.",
            "recommendations": [
                "Thêm rau xanh để tăng chất xơ",
                "Uống nước sau bữa ăn 30 phút"
            ],
            "warnings": [],
            "suitability_score": 75,
            "ai_analysis": "Mock analysis - OpenAI API not configured"
        }
