"""
Simple Health Advisor Tool - Simplified version without complex dependencies
"""
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json


class HealthAdvisorInput(BaseModel):
    """Input for health advisor tool"""
    disease: str = Field(description="Tên bệnh lý (VD: tiểu đường, cao huyết áp)")
    food_name: Optional[str] = Field(default=None, description="Tên món ăn cần phân tích")


class HealthAdvisorTool(BaseTool):
    """
    Công cụ tư vấn sức khỏe và dinh dưỡng cho người Việt Nam
    
    Chức năng:
    1. TỰ VẤN BỆNH LÝ (chỉ disease): Đưa ra lời khuyên tổng quát
    2. PHÂN TÍCH MÓN ĂN (disease + food_name): Đánh giá chi tiết món ăn có phù hợp không
    """
    
    name: str = "health_advisor"
    description: str = """Tư vấn dinh dưỡng cho người bệnh. 
    Input: disease (bắt buộc), food_name (tùy chọn)
    Output: Lời khuyên chi tiết về chế độ ăn phù hợp với bệnh lý"""
    
    args_schema: type = HealthAdvisorInput

    # Disease normalization mapping
    DISEASE_MAP: Dict[str, str] = {
        "tiểu đường": "Tiểu đường",
        "đái tháo đường": "Tiểu đường",
        "diabetes": "Tiểu đường",
        "béo phì": "Béo phì",
        "thừa cân": "Béo phì",
        "obesity": "Béo phì",
        "cao huyết áp": "Huyết áp cao",
        "huyết áp cao": "Huyết áp cao",
        "hypertension": "Huyết áp cao",
        "tim mạch": "Bệnh tim mạch",
        "bệnh tim": "Bệnh tim mạch",
    }

    def _run(self, disease: str, food_name: Optional[str] = None) -> str:
        """Execute the health advisor tool"""
        try:
            # Normalize disease name
            standardized_disease = self._normalize_disease_name(disease)
            
            if not standardized_disease:
                return self._create_error_response(disease)
            
            if food_name:
                # Analyze specific food for the disease
                return self._analyze_food_for_disease(food_name, standardized_disease)
            else:
                # General advice for the disease
                return self._get_general_advice(standardized_disease)
                
        except Exception as e:
            return f"Lỗi khi tư vấn sức khỏe: {str(e)}"

    def _normalize_disease_name(self, disease: str) -> Optional[str]:
        """Normalize disease name to standard format"""
        disease_lower = disease.lower().strip()
        return self.DISEASE_MAP.get(disease_lower)

    def _create_error_response(self, disease: str) -> str:
        """Create error response for unknown disease"""
        return json.dumps({
            "lỗi": f"Không nhận diện được bệnh lý: {disease}",
            "gợi_ý": "Các bệnh lý được hỗ trợ: tiểu đường, béo phì, cao huyết áp, bệnh tim mạch",
            "hướng_dẫn": "Vui lòng nhập tên bệnh chính xác hoặc liên hệ bác sĩ chuyên khoa"
        }, ensure_ascii=False)

    def _get_general_advice(self, disease: str) -> str:
        """Get general dietary advice for a disease"""
        advice_map = {
            "Tiểu đường": {
                "nguyên_tắc_chính": "Kiểm soát đường huyết, hạn chế carbohydrate đơn giản",
                "nên_ăn": [
                    "Rau xanh (rau muống, cải xanh, bông cải xanh)",
                    "Protein nạc (ức gà, cá, đậu hũ)",
                    "Ngũ cốc nguyên hạt (gạo lứt, yến mạch)",
                    "Các loại đậu (đậu đen, đậu xanh)"
                ],
                "tránh_ăn": [
                    "Đường trắng, bánh ngọt, kẹo",
                    "Nước ngọt có ga, nước trái cây đóng hộp",
                    "Cơm trắng, bánh mì trắng",
                    "Trái cây nhiều đường (xoài chín, mít)"
                ],
                "lưu_ý": "Ăn nhiều bữa nhỏ, kiểm soát portion size, tập thể dục đều đặn"
            },
            "Béo phì": {
                "nguyên_tắc_chính": "Giảm calo, tăng cường hoạt động thể chất",
                "nên_ăn": [
                    "Rau củ quả tươi",
                    "Protein nạc (cá, ức gà không da)",
                    "Ngũ cốc nguyên hạt",
                    "Sữa ít béo"
                ],
                "tránh_ăn": [
                    "Đồ chiên rán, fast food",
                    "Đồ uống có đường",
                    "Bánh kẹo, snack",
                    "Thịt béo, da động vật"
                ],
                "lưu_ý": "Giảm 0.5-1kg/tuần là an toàn, uống nhiều nước, ngủ đủ giấc"
            },
            "Huyết áp cao": {
                "nguyên_tắc_chính": "Giảm natrium, tăng kali, kiểm soát cân nặng",
                "nên_ăn": [
                    "Rau xanh giàu kali (rau bina, cần tây)",
                    "Trái cây (chuối, cam, táo)",
                    "Cá giàu omega-3 (cá hồi, cá thu)",
                    "Hạt không muối (hạnh nhân, óc chó)"
                ],
                "tránh_ăn": [
                    "Muối ăn, mắm tôm, nước mắm",
                    "Đồ hộp, đồ ăn sẵn",
                    "Thịt hun khói, xúc xích",
                    "Phô mai, bánh mì mặn"
                ],
                "lưu_ý": "Hạn chế muối dưới 5g/ngày, tập thể dục nhẹ nhàng, giảm stress"
            },
            "Bệnh tim mạch": {
                "nguyên_tắc_chính": "Giảm cholesterol xấu, tăng omega-3, kiểm soát cân nặng",
                "nên_ăn": [
                    "Cá béo (cá hồi, cá thu, cá trích)",
                    "Dầu olive, dầu canola",
                    "Hạt và quả khô",
                    "Yến mạch, đậu"
                ],
                "tránh_ăn": [
                    "Thịt đỏ nhiều mỡ",
                    "Đồ chiên rán",
                    "Bơ, kem, phô mai béo",
                    "Đồ ngọt, bánh kem"
                ],
                "lưu_ý": "Tập aerobic đều đặn, không hút thuốc, hạn chế rượu bia"
            }
        }
        
        advice = advice_map.get(disease, {})
        if not advice:
            return self._create_error_response(disease)
        
        return json.dumps({
            "bệnh_lý": disease,
            "tư_vấn_tổng_quát": advice,
            "khuyến_nghị": f"Nên tham khảo ý kiến bác sĩ chuyên khoa {disease.lower()} để có chế độ ăn phù hợp nhất"
        }, ensure_ascii=False, indent=2)

    def _analyze_food_for_disease(self, food_name: str, disease: str) -> str:
        """Analyze specific food for a disease"""
        # Simple nutrition database for common Vietnamese foods
        nutrition_db = {
            "phở bò": {"calories": 450, "protein": 30, "carbs": 45, "fat": 15, "sodium": 1200},
            "cơm trắng": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "sodium": 1},
            "bánh mì": {"calories": 250, "protein": 8, "carbs": 40, "fat": 8, "sodium": 400},
            "gỏi cuốn": {"calories": 60, "protein": 3, "carbs": 12, "fat": 1, "sodium": 200},
            "bún bò huế": {"calories": 500, "protein": 25, "carbs": 50, "fat": 20, "sodium": 1500},
            "cơm tấm": {"calories": 650, "protein": 35, "carbs": 70, "fat": 25, "sodium": 800},
        }
        
        # Find nutrition info (fuzzy matching)
        nutrition = None
        food_lower = food_name.lower()
        for key, data in nutrition_db.items():
            if food_lower in key or key in food_lower:
                nutrition = data
                break
        
        if not nutrition:
            return json.dumps({
                "món_ăn": food_name,
                "kết_quả": "Không tìm thấy thông tin dinh dưỡng",
                "gợi_ý": "Vui lòng cung cấp thông tin chi tiết hơn về món ăn"
            }, ensure_ascii=False)
        
        # Analyze based on disease
        analysis = self._get_food_analysis(nutrition, disease)
        
        return json.dumps({
            "món_ăn": food_name,
            "bệnh_lý": disease,
            "thông_tin_dinh_dưỡng": nutrition,
            "phân_tích": analysis,
            "khuyến_nghị": self._get_recommendations(nutrition, disease)
        }, ensure_ascii=False, indent=2)

    def _get_food_analysis(self, nutrition: Dict[str, Any], disease: str) -> Dict[str, Any]:
        """Analyze food nutrition for specific disease"""
        analysis = {"điểm_số": 50, "mức_độ_an_toàn": "Trung bình"}
        
        if disease == "Tiểu đường":
            carbs = nutrition.get("carbs", 0)
            if carbs <= 20:
                analysis["điểm_số"] = 80
                analysis["mức_độ_an_toàn"] = "An toàn"
            elif carbs <= 40:
                analysis["điểm_số"] = 60
                analysis["mức_độ_an_toàn"] = "Chấp nhận được"
            else:
                analysis["điểm_số"] = 30
                analysis["mức_độ_an_toàn"] = "Cần hạn chế"
            analysis["lý_do"] = f"Carbs: {carbs}g - {'Thấp' if carbs <= 20 else 'Cao' if carbs > 40 else 'Trung bình'}"
            
        elif disease == "Béo phì":
            calories = nutrition.get("calories", 0)
            if calories <= 200:
                analysis["điểm_số"] = 80
                analysis["mức_độ_an_toàn"] = "Tốt cho giảm cân"
            elif calories <= 400:
                analysis["điểm_số"] = 60
                analysis["mức_độ_an_toàn"] = "Ăn vừa phải"
            else:
                analysis["điểm_số"] = 30
                analysis["mức_độ_an_toàn"] = "Hạn chế"
            analysis["lý_do"] = f"Calories: {calories} - {'Thấp' if calories <= 200 else 'Cao' if calories > 400 else 'Trung bình'}"
            
        elif disease == "Huyết áp cao":
            sodium = nutrition.get("sodium", 0)
            if sodium <= 300:
                analysis["điểm_số"] = 80
                analysis["mức_độ_an_toàn"] = "An toàn"
            elif sodium <= 600:
                analysis["điểm_số"] = 50
                analysis["mức_độ_an_toàn"] = "Cần cẩn thận"
            else:
                analysis["điểm_số"] = 20
                analysis["mức_độ_an_toàn"] = "Nguy hiểm"
            analysis["lý_do"] = f"Natrium: {sodium}mg - {'Thấp' if sodium <= 300 else 'Cao' if sodium > 600 else 'Trung bình'}"
        
        return analysis

    def _get_recommendations(self, nutrition: Dict[str, Any], disease: str) -> list:
        """Get recommendations for food modification"""
        recommendations = []
        
        if disease == "Tiểu đường":
            if nutrition.get("carbs", 0) > 40:
                recommendations.append("Giảm khẩu phần xuống 1/2")
                recommendations.append("Kết hợp với rau xanh để chậm hấp thụ đường")
            recommendations.append("Ăn sau khi tập thể dục nhẹ")
            
        elif disease == "Béo phì":
            if nutrition.get("calories", 0) > 400:
                recommendations.append("Chia thành 2 bữa nhỏ")
                recommendations.append("Bỏ phần nước dùng để giảm calo")
            recommendations.append("Tăng cường rau xanh")
            
        elif disease == "Huyết áp cao":
            if nutrition.get("sodium", 0) > 600:
                recommendations.append("Không thêm muối/nước mắm")
                recommendations.append("Rửa sạch để bớt mặn")
            recommendations.append("Kết hợp với trái cây giàu kali")
        
        return recommendations