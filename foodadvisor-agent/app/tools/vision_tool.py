"""
Tool: Nhận diện ảnh món ăn Việt Nam
"""
import base64
try:
    from langchain_core.tools import BaseTool
except ImportError:
    from langchain.tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field
from openai import OpenAI
from app.config import settings
import json


class VisionToolInput(BaseModel):
    image_path: str = Field(description="Đường dẫn đến file ảnh hoặc base64 encoded image")
    is_base64: bool = Field(default=False, description="True nếu image_path là base64 string")


class VisionTool(BaseTool):
    """
    Tool nhận diện món ăn Việt Nam từ ảnh
    Sử dụng OpenAI Vision API hoặc ViT model để nhận diện
    """
    name: str = "vision_tool"
    description: str = """
    Nhận diện món ăn Việt Nam và thành phần từ ảnh bữa ăn.
    Trả về tên món, danh sách thành phần chính, và ước tính khẩu phần.
    Ví dụ: Phở bò, Cơm tấm sườn nướng, Gỏi cuốn, Bún bò Huế, etc.
    """
    args_schema: Type[BaseModel] = VisionToolInput
    
    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        
        # Danh sách món ăn Việt Nam phổ biến để cải thiện độ chính xác
        self.vietnamese_foods = [
            "phở bò", "phở gà", "bún bò Huế", "bún riêu", "bún chả",
            "cơm tấm", "cơm gà", "cơm rang", "gỏi cuốn", "bánh xèo",
            "bánh mì", "bánh cuốn", "chả giò", "nem nướng", "bò kho",
            "canh chua", "canh khổ qua", "thịt kho tàu", "cá kho tộ"
        ]
    
    def _run(self, image_path: str, is_base64: bool = False) -> str:
        """
        Xử lý ảnh và trả về thông tin món ăn Việt Nam được nhận diện
        """
        try:
            # Đọc ảnh
            if is_base64:
                image_data = image_path
            else:
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Sử dụng OpenAI Vision API
            if self.client:
                return self._recognize_with_openai(image_data, is_base64)
            else:
                # Fallback: Sử dụng logic cơ bản hoặc model khác
                return self._recognize_basic(image_path)
                
        except Exception as e:
            return f"Lỗi khi nhận diện ảnh: {str(e)}"
    
    def _recognize_with_openai(self, image_data: str, is_base64: bool) -> str:
        """Nhận diện với OpenAI Vision API"""
        try:
            prompt = f"""
            Bạn là chuyên gia nhận diện món ăn Việt Nam. Hãy phân tích ảnh này và trả về JSON với format:
            {{
                "dish_name": "Tên món ăn tiếng Việt",
                "dish_name_en": "Tên tiếng Anh (nếu có)",
                "category": "phở/bún/cơm/gỏi/bánh/canh/etc",
                "region": "Bắc/Trung/Nam (nếu xác định được)",
                "main_ingredients": ["thành phần 1", "thành phần 2", ...],
                "estimated_weight_g": ước tính khối lượng (gram),
                "confidence": độ tin cậy (0-1)
            }}
            
            Tập trung nhận diện các món ăn Việt Nam phổ biến: {', '.join(self.vietnamese_foods[:10])}
            """
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}" if is_base64 else image_data
                            }
                        }
                    ]
                }
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            return result
            
        except Exception as e:
            return f"Lỗi OpenAI Vision API: {str(e)}"
    
    def _recognize_basic(self, image_path: str) -> str:
        """Nhận diện cơ bản (fallback)"""
        # TODO: Implement với local ViT model hoặc YOLOv9
        return json.dumps({
            "dish_name": "Món ăn Việt Nam (cần model nhận diện)",
            "category": "unknown",
            "main_ingredients": [],
            "estimated_weight_g": 0,
            "confidence": 0.0
        })

