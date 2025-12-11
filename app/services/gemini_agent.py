"""
Gemini-based Food Advisor Agent
"""
import os
import json
import google.generativeai as genai
from typing import Optional
from app.config import settings


class GeminiAgent:
    """Food Advisor Agent sử dụng Google Gemini"""
    
    def __init__(self):
        """Initialize Gemini agent"""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Load few-shot prompt
        self.few_shot_prompt = self._load_few_shot_prompt()
    
    def _load_few_shot_prompt(self) -> str:
        """Load few-shot prompt từ file"""
        prompt_file = "training_data/gemini_few_shot_prompt.txt"
        
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Default prompt nếu chưa có training
        return """Bạn là Food Advisor AI - chuyên gia tư vấn dinh dưỡng và món ăn Việt Nam.

Nhiệm vụ:
- Phân tích dinh dưỡng món ăn Việt Nam
- Gợi ý món ăn phù hợp với sức khỏe
- Tính toán calo và thành phần dinh dưỡng
- Tư vấn chế độ ăn cho người bệnh

Phong cách:
- Chuyên nghiệp, chính xác
- Thân thiện, dễ hiểu
- Cung cấp thông tin chi tiết
- Có ví dụ cụ thể
"""
    
    def query(self, user_query: str, context: Optional[dict] = None) -> str:
        """
        Query agent với user input
        
        Args:
            user_query: Câu hỏi của user
            context: Context bổ sung (optional)
        
        Returns:
            Response từ agent
        """
        # Build full prompt
        full_prompt = self.few_shot_prompt + "\n\n"
        
        # Add context nếu có
        if context:
            full_prompt += f"Context: {json.dumps(context, ensure_ascii=False)}\n\n"
        
        full_prompt += f"User: {user_query}\n\nAssistant:"
        
        # Call Gemini
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def analyze_food(self, food_name: str) -> dict:
        """
        Phân tích dinh dưỡng món ăn
        
        Args:
            food_name: Tên món ăn
        
        Returns:
            Dict chứa thông tin dinh dưỡng
        """
        query = f"Phân tích chi tiết dinh dưỡng món {food_name}"
        response = self.query(query)
        
        return {
            'food_name': food_name,
            'analysis': response
        }
    
    def suggest_food(self, health_condition: str, preferences: Optional[list] = None) -> dict:
        """
        Gợi ý món ăn phù hợp
        
        Args:
            health_condition: Tình trạng sức khỏe
            preferences: Sở thích (optional)
        
        Returns:
            Dict chứa gợi ý món ăn
        """
        query = f"Gợi ý món ăn Việt Nam cho người {health_condition}"
        
        if preferences:
            query += f". Sở thích: {', '.join(preferences)}"
        
        response = self.query(query)
        
        return {
            'health_condition': health_condition,
            'suggestions': response
        }
    
    def calculate_calories(self, food_name: str, portion: Optional[str] = None) -> dict:
        """
        Tính calo món ăn
        
        Args:
            food_name: Tên món ăn
            portion: Khẩu phần (optional)
        
        Returns:
            Dict chứa thông tin calo
        """
        query = f"Tính calo món {food_name}"
        
        if portion:
            query += f" với khẩu phần {portion}"
        
        response = self.query(query)
        
        return {
            'food_name': food_name,
            'portion': portion,
            'calories': response
        }


# Global instance
gemini_agent = GeminiAgent()
