"""
Health Advisor Tool - Unified health consultation for Vietnamese diseases
Combines general health advice and specific food analysis
"""
from typing import Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from app.utils.database_helpers import DatabaseHelpers
import json


class HealthAdvisorInput(BaseModel):
    """Input schema for Health Advisor Tool"""
    disease: str = Field(..., description="Tên bệnh: tiểu đường, béo phì, huyết áp cao")
    food_name: Optional[str] = Field(default=None, description="Tên món ăn cần phân tích (optional)")
    portion_size: Optional[str] = Field(default="1 phần", description="Khẩu phần ăn")


class HealthAdvisorTool(BaseTool):
    """
    Unified Health Advisor Tool for Vietnamese diseases
    
    Supports two modes:
    1. General advice: disease only
    2. Food analysis: disease + food_name
    """
    name: str = "health_advisor_tool"
    description: str = """Tool tư vấn sức khỏe toàn diện cho 3 bệnh phổ biến nhất ở Việt Nam:
• Tiểu đường (đái tháo đường)
• Béo phì  
• Huyết áp cao (tăng huyết áp)

2 chế độ hoạt động:
1. TƯ VẤN TỔNG QUAN (chỉ cần disease): Lời khuyên chung, thực phẩm nên/tránh
2. PHÂN TÍCH MÓN ĂN (disease + food_name): Đánh giá chi tiết món ăn có phù hợp không"""
    
    args_schema: type = HealthAdvisorInput

    # Disease normalization mapping
    DISEASE_MAP: dict = {
        "tiểu đường": "Tiểu đường",
        "đái tháo đường": "Tiểu đường",
        "đường huyết cao": "Tiểu đường",
        "diabetes": "Tiểu đường",
        "béo": "Béo phì",
        "béo phì": "Béo phì",
        "thừa cân": "Béo phì",
        "obesity": "Béo phì",
        "huyết áp": "Huyết áp cao",
        "tăng huyết áp": "Huyết áp cao",
        "cao huyết áp": "Huyết áp cao",
        "huyết áp cao": "Huyết áp cao",
        "hypertension": "Huyết áp cao"
    }

    def _run(
        self, 
        disease: str, 
        food_name: Optional[str] = None, 
        portion_size: str = "1 phần"
    ) -> str:
        """
        Main execution method
        
        Args:
            disease: Disease name
            food_name: Food name for analysis (optional)
            portion_size: Portion size
            
        Returns:
            JSON string with health advice or food analysis
        """
        # Normalize disease name
        standardized_disease = self._normalize_disease_name(disease)
        if not standardized_disease:
            return self._create_error_response(disease)
        
        # Determine mode based on input
        if food_name and food_name.strip():
            return self._analyze_food_for_disease(standardized_disease, food_name, portion_size)
        else:
            return self._get_general_health_advice(standardized_disease)

    def _normalize_disease_name(self, disease: str) -> Optional[str]:
        """Normalize disease name using mapping"""
        return self.DISEASE_MAP.get(disease.strip().lower())

    def _create_error_response(self, disease: str) -> str:
        """Create standardized error response"""
        return json.dumps({
            "lỗi": "Hiện tại chỉ hỗ trợ 3 bệnh: Tiểu đường, Béo phì, Huyết áp cao",
            "bạn_nhập": disease,
            "gợi_ý": "Hãy nhập: 'tiểu đường', 'béo phì', hoặc 'huyết áp cao'"
        }, ensure_ascii=False, indent=2)

    def _get_general_health_advice(self, disease: str) -> str:
        """Tư vấn sức khỏe tổng quan cho bệnh"""
        
        # Lấy thông tin từ database
        disease_rules = DatabaseHelpers.get_disease_rules(disease)
        suitable_foods = DatabaseHelpers.get_suitable_foods_for_disease(disease, limit=5)
        
        # Tạo kết quả tư vấn
        result = {
            "bệnh": disease,
            "cảnh_báo_nặng_nhất": self._get_critical_nutrients(disease),
            "lời_khuyên_ngắn_gọn": self._get_disease_advice(disease),
            "hạn_chế_nghiêm_ngặt": self._get_restricted_foods(disease),
            "nên_ăn_nhiều": self._get_recommended_foods(disease),
            "calo_tối_đa_mỗi_bữa": self._get_max_calories_per_meal(disease),
            "thực_phẩm_an_toàn_hôm_nay": suitable_foods
        }
        
        # Thêm thông tin từ database nếu có
        if disease_rules:
            if disease_rules.get("guidelines"):
                guidelines = disease_rules["guidelines"]
                result["hướng_dẫn_chi_tiết"] = guidelines[:300] + "..." if len(guidelines) > 300 else guidelines
            
            if disease_rules.get("foods_to_avoid"):
                result["tránh_hoàn_toàn"] = disease_rules["foods_to_avoid"][:5]
            
            if disease_rules.get("recommended_foods"):
                result["khuyến_khích"] = disease_rules["recommended_foods"][:5]
            
            if disease_rules.get("max_daily_calories"):
                result["giới_hạn_calo_ngày"] = disease_rules["max_daily_calories"]
        
        return json.dumps(result, ensure_ascii=False, indent=2)

    def _analyze_food_for_disease(self, disease: str, food_name: str, portion_size: str) -> str:
        """Phân tích chi tiết món ăn cho bệnh lý"""
        
        # Lấy thông tin dinh dưỡng từ database
        nutrition_info = DatabaseHelpers.get_food_nutrition(food_name)
        
        if not nutrition_info:
            # Fallback với database cứng
            nutrition_info = self._get_fallback_nutrition(food_name)
        
        if not nutrition_info:
            return json.dumps({
                "lỗi": f"Không tìm thấy thông tin dinh dưỡng cho '{food_name}'",
                "gợi_ý": "Thử với tên món ăn khác như: phở bò, cơm tấm, bánh mì, gỏi cuốn"
            }, ensure_ascii=False, indent=2)
        
        # Phân tích theo bệnh lý
        analysis_result = {
            "thông_tin_món_ăn": {
                "tên": food_name,
                "khẩu_phần": portion_size,
                "dinh_dưỡng_chi_tiết": nutrition_info
            },
            "phân_tích_cho_bệnh": disease,
            "đánh_giá_từng_chất": {},
            "mức_độ_an_toàn": "",
            "điểm_số": 0,
            "lời_khuyên_cụ_thể": [],
            "cách_điều_chỉnh": []
        }
        
        # Tính điểm an toàn
        score = self._calculate_safety_score(nutrition_info, disease)
        analysis_result["điểm_số"] = score
        
        # Đánh giá mức độ an toàn
        if score >= 80:
            analysis_result["mức_độ_an_toàn"] = "RẤT AN TOÀN ✅"
            analysis_result["lời_khuyên_cụ_thể"].append("Món ăn này rất phù hợp với bệnh lý của bạn")
        elif score >= 60:
            analysis_result["mức_độ_an_toàn"] = "CHẤP NHẬN ĐƯỢC ⚠️"
            analysis_result["lời_khuyên_cụ_thể"].append("Có thể ăn nhưng cần hạn chế khẩu phần")
        else:
            analysis_result["mức_độ_an_toàn"] = "KHÔNG NÊN ĂN ❌"
            analysis_result["lời_khuyên_cụ_thể"].append("Nên tránh món ăn này")
        
        # Phân tích từng chất dinh dưỡng
        analysis_result["đánh_giá_từng_chất"] = self._analyze_nutrients_for_disease(nutrition_info, disease)
        
        # Gợi ý điều chỉnh
        analysis_result["cách_điều_chỉnh"] = self._get_adjustment_suggestions(nutrition_info, disease)
        
        return json.dumps(analysis_result, ensure_ascii=False, indent=2)

    def _calculate_safety_score(self, nutrition: dict, disease: str) -> int:
        """Tính điểm an toàn cho món ăn theo bệnh lý"""
        score = 50  # Base score
        
        calories = nutrition.get("calories", 0) or 0
        carbs = nutrition.get("carbs", 0) or 0
        fat = nutrition.get("fat", 0) or 0
        protein = nutrition.get("protein", 0) or 0
        
        if disease == "Tiểu đường":
            # Carbs analysis
            if carbs <= 30:
                score += 20
            elif carbs <= 50:
                score += 10
            else:
                score -= 20
            
            # Protein bonus
            if protein >= 15:
                score += 15
            
            # Calories check
            if calories <= 400:
                score += 15
        
        elif disease == "Béo phì":
            # Calories analysis
            if calories <= 200:
                score += 25
            elif calories <= 400:
                score += 10
            else:
                score -= 25
            
            # Fat analysis
            if fat <= 10:
                score += 15
            elif fat <= 20:
                score += 5
            else:
                score -= 15
        
        elif disease == "Huyết áp cao":
            # Sodium would be ideal but not always available
            # Use general healthy food principles
            if calories <= 300:
                score += 15
            
            if protein >= 10:
                score += 10
            
            # Assume low sodium if it's a healthy food
            if nutrition.get("category") in ["rau", "trái cây", "cá"]:
                score += 20
        
        return max(0, min(100, score))

    def _analyze_nutrients_for_disease(self, nutrition: dict, disease: str) -> dict:
        """Phân tích từng chất dinh dưỡng theo bệnh"""
        analysis = {}
        
        calories = nutrition.get("calories", 0) or 0
        carbs = nutrition.get("carbs", 0) or 0
        fat = nutrition.get("fat", 0) or 0
        protein = nutrition.get("protein", 0) or 0
        
        if disease == "Tiểu đường":
            # Carbs analysis
            if carbs <= 30:
                status = "AN TOÀN"
            elif carbs <= 50:
                status = "CHẤP NHẬN ĐƯỢC"
            else:
                status = "NGUY HIỂM"
            
            analysis["carbohydrate"] = {
                "giá_trị": f"{carbs}g",
                "giới_hạn": "< 50g/bữa",
                "trạng_thái": status,
                "lý_do": "Carbs cao làm tăng đường huyết"
            }
        
        elif disease == "Béo phì":
            # Calories analysis
            if calories <= 200:
                status = "ÍT CALO"
            elif calories <= 400:
                status = "TRUNG BÌNH"
            else:
                status = "NHIỀU CALO"
            
            analysis["calo"] = {
                "giá_trị": f"{calories} kcal",
                "trạng_thái": status,
                "lý_do": "Calo cao dẫn đến tăng cân"
            }
        
        elif disease == "Huyết áp cao":
            # General health analysis
            analysis["tổng_quan"] = {
                "giá_trị": f"{calories} kcal, {protein}g protein",
                "trạng_thái": "CẦN KIỂM TRA MUỐI",
                "lý_do": "Cần tránh muối và thực phẩm chế biến sẵn"
            }
        
        return analysis

    def _get_adjustment_suggestions(self, nutrition: dict, disease: str) -> list:
        """Gợi ý cách điều chỉnh món ăn"""
        suggestions = []
        
        calories = nutrition.get("calories", 0) or 0
        carbs = nutrition.get("carbs", 0) or 0
        
        if disease == "Tiểu đường":
            if carbs > 45:
                suggestions.append("Giảm khẩu phần xuống 1/2")
                suggestions.append("Ăn kèm rau xanh để tăng chất xơ")
            suggestions.append("Thay cơm trắng bằng gạo lứt nếu có")
        
        elif disease == "Béo phì":
            if calories > 400:
                suggestions.append("Giảm khẩu phần xuống 2/3")
                suggestions.append("Tăng rau xanh, giảm carbs")
            suggestions.append("Chọn phương pháp nấu hấp, luộc thay vì chiên")
        
        elif disease == "Huyết áp cao":
            suggestions.append("Yêu cầu nấu ít muối hoặc không muối")
            suggestions.append("Không thêm nước mắm, tương ớt")
            suggestions.append("Ăn kèm chuối hoặc rau giàu kali")
        
        return suggestions

    def _get_fallback_nutrition(self, food_name: str) -> Optional[dict]:
        """Database dinh dưỡng cứng cho các món phổ biến"""
        food_db = {
            "phở bò": {"calories": 450, "protein": 30, "carbs": 45, "fat": 15, "category": "phở"},
            "cơm trắng": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "category": "cơm"},
            "bánh mì": {"calories": 400, "protein": 15, "carbs": 50, "fat": 18, "category": "bánh"},
            "gỏi cuốn": {"calories": 60, "protein": 5, "carbs": 8, "fat": 2, "category": "gỏi"},
            "cơm tấm": {"calories": 650, "protein": 35, "carbs": 70, "fat": 22, "category": "cơm"},
            "bún bò huế": {"calories": 550, "protein": 28, "carbs": 55, "fat": 20, "category": "bún"},
            "bánh xèo": {"calories": 350, "protein": 12, "carbs": 40, "fat": 16, "category": "bánh"},
            "cháo gà": {"calories": 280, "protein": 20, "carbs": 35, "fat": 8, "category": "cháo"}
        }
        
        # Fuzzy matching
        food_name_lower = food_name.lower()
        for key, data in food_db.items():
            if food_name_lower in key or key in food_name_lower:
                return data
        
        return None

    def _get_critical_nutrients(self, disease: str) -> list:
        """Những chất ảnh hưởng nặng nhất theo từng bệnh"""
        if disease == "Tiểu đường":
            return ["Đường", "Tinh bột tinh chế", "Cơm trắng", "Nước ngọt", "Bánh kẹo"]
        elif disease == "Béo phì":
            return ["Chất béo bão hòa", "Đồ chiên rán", "Đồ ăn nhanh", "Nước ngọt có gas", "Bơ thực vật"]
        elif disease == "Huyết áp cao":
            return ["Muối", "Mắm", "Thịt hun khói", "Đồ hộp", "Nước mắm công nghiệp"]
        return []

    def _get_disease_advice(self, disease: str) -> str:
        """Lời khuyên ngắn gọn cho từng bệnh"""
        if disease == "Tiểu đường":
            return "Ăn ít đường, nhiều chất xơ. Chia nhỏ bữa ăn. Kiểm tra đường huyết thường xuyên."
        elif disease == "Béo phì":
            return "Giảm calo, tăng vận động. Ăn nhiều rau, ít chất béo. Uống nhiều nước."
        elif disease == "Huyết áp cao":
            return "Hạn chế muối, tăng kali. Ăn nhiều rau quả. Tránh căng thẳng."
        return "Tham khảo ý kiến bác sĩ chuyên khoa."

    def _get_restricted_foods(self, disease: str) -> list:
        """Thực phẩm cần hạn chế nghiêm ngặt"""
        if disease == "Tiểu đường":
            return ["Bánh ngọt", "Nước ngọt", "Cơm trắng", "Bánh mì trắng", "Kẹo", "Mật ong", "Trái cây ngọt"]
        elif disease == "Béo phì":
            return ["Đồ chiên", "Bánh kẹo", "Nước ngọt", "Thức ăn nhanh", "Kem", "Bánh quy", "Đồ uống có cồn"]
        elif disease == "Huyết áp cao":
            return ["Muối ăn", "Nước mắm", "Tương ớt", "Thịt hun khói", "Đồ hộp", "Mì gói", "Bánh tráng nướng"]
        return []

    def _get_recommended_foods(self, disease: str) -> list:
        """Thực phẩm nên ăn nhiều"""
        if disease == "Tiểu đường":
            return ["Rau xanh", "Cá", "Trứng", "Yến mạch", "Đậu", "Quả bơ", "Hạt óc chó"]
        elif disease == "Béo phì":
            return ["Rau củ", "Trái cây ít đường", "Cá", "Ức gà", "Đậu", "Yến mạch", "Nước lọc"]
        elif disease == "Huyết áp cao":
            return ["Chuối", "Rau bina", "Cá hồi", "Yến mạch", "Đậu đen", "Hạt lanh", "Trà xanh"]
        return []

    def _get_max_calories_per_meal(self, disease: str) -> int:
        """Calo tối đa mỗi bữa ăn"""
        if disease == "Tiểu đường":
            return 500  # Chia nhỏ bữa ăn
        elif disease == "Béo phì":
            return 400  # Hạn chế calo
        elif disease == "Huyết áp cao":
            return 600  # Bình thường nhưng ít muối
        return 500