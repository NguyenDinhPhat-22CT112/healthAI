"""
Simple Food Advisor Agent - Trả lời tự nhiên hơn
Không dùng ReAct pattern phức tạp, chỉ dùng tools khi thực sự cần
"""
from typing import List, Optional, Dict, Any, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.tools import BaseTool
from app.config import settings
import json
import re


class SimpleFoodAgent:
    """Agent đơn giản, trả lời tự nhiên như con người"""
    
    def __init__(
        self,
        tools: List[BaseTool],
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
    ):
        self.tools = tools
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=settings.openai_api_key,
        )
        
        # Tạo mapping tools để dễ gọi
        self.tool_map = {tool.name: tool for tool in tools}
        
        # System prompt tự nhiên theo phong cách Huấn luyện viên Minh Anh
        self.system_prompt = """Bạn là Huấn luyện viên Sức khỏe Minh Anh, một chuyên gia tư vấn dinh dưỡng trực tuyến chuyên về ẩm thực Việt Nam. Vai trò của bạn là cung cấp lời khuyên ăn uống dựa trên bệnh lý (Tiểu đường, Huyết áp cao, Béo phì) một cách chính xác, dễ hiểu, và đầy cảm hứng.

🎯 QUY TẮC PHONG CÁCH TỰ NHIÊN:
• **Tông điệu**: Ấm áp, đồng cảm, khuyến khích. Luôn thể hiện sự quan tâm đến cảm xúc của người bệnh.
• **Xưng hô**: Dùng "Tôi" và "Bạn" để xây dựng mối quan hệ đồng hành.
• **Cấu trúc**: Phá vỡ văn bản bằng tiêu đề in đậm và danh sách gạch đầu dòng. Tránh dùng câu quá dài và phức tạp.
• **Mở lời**: Bắt đầu bằng một câu chào tự nhiên và tích cực, tránh các câu khô khan như "Tôi đã nhận được yêu cầu của bạn..."

🏥 QUY TẮC NỘI DUNG CHUYÊN MÔN:
• **Thực tiễn**: Mỗi lời khuyên phải đi kèm với ví dụ thực phẩm cụ thể hoặc mẹo nấu ăn đơn giản.
• **Cảnh báo an toàn** (RẤT QUAN TRỌNG): Luôn đưa ra câu từ chối trách nhiệm, nhắc nhở người dùng rằng lời khuyên này mang tính chất tham khảo và không thay thế lời khuyên từ bác sĩ hoặc chuyên gia dinh dưỡng lâm sàng.
• **Kết thúc**: Luôn kết thúc bằng một lời động viên và một câu hỏi gợi mở để mời người dùng tiếp tục cuộc trò chuyện.

🧠 KIẾN THỨC CHUYÊN MÔN:
• Ẩm thực 3 miền Bắc-Trung-Nam Việt Nam
• Dinh dưỡng món Việt (phở, bún, cơm, bánh xèo, gỏi cuốn...)
• Tư vấn chuyên sâu cho: Tiểu đường, Huyết áp cao, Béo phì
• Công thức nấu ăn truyền thống và hiện đại

🛠️ TOOLS AVAILABLE (chỉ dùng khi cần):
• health_advisor_tool: Tư vấn sức khỏe và phân tích món ăn chi tiết
• recipe_generator_tool: Tạo công thức từ nguyên liệu có sẵn
• vision_tool: Nhận diện món ăn từ ảnh

💡 CÁCH TRẢ LỜI:
1. **Chào hỏi ấm áp**: Bắt đầu với lời chào tự nhiên, thể hiện sự quan tâm
2. **Nội dung chính**: Chia thành các phần rõ ràng với tiêu đề in đậm
3. **Ví dụ thực tế**: Đưa ra món ăn cụ thể, cách chế biến đơn giản
4. **Cảnh báo an toàn**: Nhắc nhở tính chất tham khảo
5. **Kết thúc tích cực**: Động viên và đặt câu hỏi gợi mở

Hãy trò chuyện như một người bạn đồng hành trong hành trình chăm sóc sức khỏe!"""

    def _should_use_tool(self, query: str) -> Tuple[Optional[str], Optional[dict]]:
        """Quyết định có nên dùng tool không và tool nào"""
        query_lower = query.lower()
        
        # Patterns cho health advisor
        health_patterns = [
            r'(tiểu đường|đái tháo đường|diabetes)',
            r'(béo phì|thừa cân|obesity)',
            r'(huyết áp cao|tăng huyết áp|hypertension)',
            r'(phân tích|đánh giá).+(món|thức ăn|đồ ăn)',
            r'(ăn|uống).+(có được không|được không|có tốt)',
            r'(tư vấn|khuyên).+(sức khỏe|bệnh)',
        ]
        
        # Patterns cho recipe generator
        recipe_patterns = [
            r'(công thức|cách làm|cách nấu)',
            r'(gợi ý|đề xuất).+(món|công thức)',
            r'(tôi có|có sẵn).+(nguyên liệu|thịt|rau|cá)',
            r'(làm gì|nấu gì).+(với|từ)',
            r'(món ăn|thức ăn).+(từ|với)',
        ]
        
        # Patterns cho vision
        vision_patterns = [
            r'(phân tích|nhận diện|xem).+(ảnh|hình|bức)',
            r'(ảnh|hình|photo|image)',
            r'(món này|đây là món gì)',
        ]
        
        # Check health advisor
        for pattern in health_patterns:
            if re.search(pattern, query_lower):
                # Extract disease and food if mentioned
                disease = None
                food_name = None
                
                if re.search(r'tiểu đường|đái tháo đường|diabetes', query_lower):
                    disease = 'tiểu đường'
                elif re.search(r'béo phì|thừa cân|obesity', query_lower):
                    disease = 'béo phì'
                elif re.search(r'huyết áp cao|tăng huyết áp|hypertension', query_lower):
                    disease = 'huyết áp cao'
                
                # Try to extract food name (simple approach)
                food_words = ['phở', 'bún', 'cơm', 'bánh', 'thịt', 'cá', 'rau', 'trứng', 'sữa', 'chả']
                for food in food_words:
                    if food in query_lower:
                        food_name = food
                        break
                
                params = {'disease': disease or 'tổng quát'}
                if food_name:
                    params['food_name'] = food_name
                    
                return 'health_advisor_tool', params
        
        # Check recipe generator
        for pattern in recipe_patterns:
            if re.search(pattern, query_lower):
                # Extract ingredients (simple approach)
                ingredients = []
                ingredient_words = ['thịt heo', 'thịt bò', 'gà', 'cá', 'tôm', 'rau muống', 'cải', 'cà chua', 'hành', 'tỏi']
                for ingredient in ingredient_words:
                    if ingredient in query_lower:
                        ingredients.append(ingredient)
                
                params = {
                    'ingredients': ', '.join(ingredients) if ingredients else 'nguyên liệu có sẵn',
                    'dietary_restrictions': None,
                    'region_preference': 'vietnamese',
                    'meal_type': None,
                    'max_calories': None
                }
                return 'recipe_generator_tool', params
        
        # Check vision
        for pattern in vision_patterns:
            if re.search(pattern, query_lower):
                return 'vision_tool', {'image_description': query}
        
        return None, None

    def _call_tool(self, tool_name: str, params: dict) -> str:
        """Gọi tool và trả về kết quả"""
        try:
            if tool_name not in self.tool_map:
                return f"Không tìm thấy tool {tool_name}"
            
            tool = self.tool_map[tool_name]
            
            if tool_name == 'health_advisor_tool':
                result = tool._run(
                    disease=params.get('disease', ''),
                    food_name=params.get('food_name'),
                    portion_size=params.get('portion_size', '1 phần')
                )
            elif tool_name == 'recipe_generator_tool':
                result = tool._run(
                    ingredients=params.get('ingredients', ''),
                    disease=params.get('disease'),
                    dietary_restrictions=params.get('dietary_restrictions'),
                    region_preference=params.get('region_preference'),
                    meal_type=params.get('meal_type'),
                    max_calories=params.get('max_calories')
                )
            elif tool_name == 'vision_tool':
                result = tool._run(image_description=params.get('image_description', ''))
            else:
                result = tool._run(**params)
            
            return result
            
        except Exception as e:
            return f"Lỗi khi gọi tool: {str(e)}"

    def _format_tool_result(self, tool_name: str, result: str, original_query: str) -> str:
        """Format kết quả tool thành câu trả lời tự nhiên"""
        try:
            # Parse JSON result if possible
            if result.startswith('{') and result.endswith('}'):
                data = json.loads(result)
                
                if tool_name == 'health_advisor_tool':
                    return self._format_health_advice(data, original_query)
                elif tool_name == 'recipe_generator_tool':
                    return self._format_recipe(data, original_query)
                elif tool_name == 'vision_tool':
                    return self._format_vision_result(data, original_query)
            
            # Fallback: return raw result with friendly intro
            return f"Dựa trên thông tin tôi có:\n\n{result}"
            
        except:
            return f"Tôi đã tìm hiểu và đây là thông tin:\n\n{result}"

    def _format_health_advice(self, data: dict, query: str) -> str:
        """Format lời khuyên sức khỏe theo phong cách Huấn luyện viên Minh Anh"""
        if 'lỗi' in data:
            return f"Chào bạn! Tôi hiểu bạn đang quan tâm đến vấn đề này. Tuy nhiên, {data['lỗi'].lower()}. {data.get('gợi_ý', '')} Bạn có thể hỏi tôi về những vấn đề khác không?"
        
        response = []
        
        # Mở đầu ấm áp
        response.append("Chào bạn! Tôi rất vui được hỗ trợ bạn về vấn đề dinh dưỡng này.")
        
        if 'bệnh' in data:
            response.append(f"\n**🏥 Về tình trạng {data['bệnh']}:**")
        
        if 'thông_tin_món_ăn' in data:
            food_info = data['thông_tin_món_ăn']
            response.append(f"\n**🍽️ Phân tích món {food_info.get('tên', 'này')}:**")
            response.append(f"• **Mức độ phù hợp**: {data.get('mức_độ_an_toàn', 'Cần đánh giá thêm')}")
            response.append(f"• **Điểm đánh giá**: {data.get('điểm_số', 'N/A')}/100 điểm")
            
            if 'lời_khuyên_cụ_thể' in data and data['lời_khuyên_cụ_thể']:
                response.append(f"\n**💡 Lời khuyên từ tôi:**")
                for i, advice in enumerate(data['lời_khuyên_cụ_thể'][:3], 1):
                    response.append(f"{i}. {advice}")
            
            if 'cách_điều_chỉnh' in data and data['cách_điều_chỉnh']:
                response.append(f"\n**🔧 Mẹo điều chỉnh thực tế:**")
                for i, adjustment in enumerate(data['cách_điều_chỉnh'][:2], 1):
                    response.append(f"{i}. {adjustment}")
        else:
            # General advice
            if 'lời_khuyên_ngắn_gọn' in data:
                response.append(f"\n**💡 Nguyên tắc chính:**\n{data['lời_khuyên_ngắn_gọn']}")
            
            if 'nên_ăn_nhiều' in data and data['nên_ăn_nhiều']:
                response.append(f"\n**✅ Thực phẩm bạn nên ưu tiên:**")
                for food in data['nên_ăn_nhiều'][:5]:
                    response.append(f"• {food}")
            
            if 'hạn_chế_nghiêm_ngặt' in data and data['hạn_chế_nghiêm_ngặt']:
                response.append(f"\n**🚫 Thực phẩm nên hạn chế:**")
                for food in data['hạn_chế_nghiêm_ngặt'][:5]:
                    response.append(f"• {food}")
            
            if 'calo_tối_đa_mỗi_bữa' in data:
                response.append(f"\n**🍽️ Khuyến nghị calo:** Tối đa {data['calo_tối_đa_mỗi_bữa']} kcal/bữa")
        
        # Cảnh báo an toàn
        response.append(f"\n**⚠️ Lưu ý quan trọng:** Lời khuyên này mang tính chất tham khảo và không thay thế lời khuyên từ bác sĩ hoặc chuyên gia dinh dưỡng lâm sàng. Bạn nên tham khảo ý kiến chuyên gia để có kế hoạch dinh dưỡng phù hợp nhất.")
        
        # Kết thúc tích cực
        response.append(f"\n**🌟 Động viên:** Việc quan tâm đến chế độ ăn uống là bước đầu tuyệt vời cho sức khỏe! Bạn có muốn tôi tư vấn thêm về món ăn nào khác hoặc cách chế biến phù hợp không?")
        
        return ''.join(response)

    def _format_recipe(self, data: dict, query: str) -> str:
        """Format công thức nấu ăn theo phong cách Huấn luyện viên Minh Anh"""
        if 'error' in data:
            return f"Chào bạn! Tôi hiểu bạn muốn có công thức từ những nguyên liệu có sẵn. Tuy nhiên, hiện tại tôi gặp chút khó khăn kỹ thuật: {data['error']}. Bạn có thể mô tả chi tiết hơn về nguyên liệu và sở thích để tôi tư vấn trực tiếp không?"
        
        response = []
        
        # Mở đầu ấm áp
        response.append("Tuyệt vời! Tôi rất thích việc bạn muốn tự tay nấu nướng. Đây là món tôi gợi ý cho bạn:")
        
        if 'recipe_name' in data:
            response.append(f"\n**🍳 Món ăn: {data['recipe_name']}**")
        
        if 'ingredients' in data and data['ingredients']:
            response.append(f"\n**📝 Nguyên liệu cần chuẩn bị:**")
            for i, ingredient in enumerate(data['ingredients'][:8], 1):
                response.append(f"{i}. {ingredient}")
        
        if 'instructions' in data and data['instructions']:
            response.append(f"\n**👩‍🍳 Cách thực hiện từng bước:**")
            for i, step in enumerate(data['instructions'][:6], 1):
                response.append(f"**Bước {i}:** {step}")
        
        # Thông tin bổ sung
        info_parts = []
        if 'cooking_time' in data:
            info_parts.append(f"⏰ {data['cooking_time']} phút")
        if 'servings' in data:
            info_parts.append(f"👥 {data['servings']} người ăn")
        
        if info_parts:
            response.append(f"\n**📊 Thông tin:** {' | '.join(info_parts)}")
        
        if 'health_benefits' in data and data['health_benefits']:
            response.append(f"\n**💚 Lợi ích sức khỏe:**")
            for benefit in data['health_benefits'][:3]:
                response.append(f"• {benefit}")
        
        # Cảnh báo an toàn
        response.append(f"\n**⚠️ Lưu ý:** Công thức này mang tính chất tham khảo. Nếu bạn có bệnh lý đặc biệt, hãy tham khảo ý kiến bác sĩ về chế độ ăn phù hợp.")
        
        # Kết thúc tích cực
        response.append(f"\n**🌟 Chúc mừng bạn:** Việc tự nấu ăn là cách tuyệt vời để kiểm soát dinh dưỡng! Bạn có cần tôi tư vấn thêm về cách điều chỉnh món này cho phù hợp với tình trạng sức khỏe cụ thể không?")
        
        return ''.join(response)

    def _format_vision_result(self, data: dict, query: str) -> str:
        """Format kết quả nhận diện ảnh"""
        return f"Tôi thấy trong ảnh có vẻ là món ăn Việt Nam. Tuy nhiên, để phân tích chính xác hơn, bạn có thể mô tả chi tiết món ăn hoặc hỏi tôi về dinh dưỡng của món cụ thể nào đó nhé! 😊"

    def chat(self, query: str, context: Optional[dict] = None) -> str:
        """Main chat method - trả lời tự nhiên"""
        try:
            # Quyết định có dùng tool không
            tool_name, tool_params = self._should_use_tool(query)
            
            if tool_name and tool_params:
                # Dùng tool
                tool_result = self._call_tool(tool_name, tool_params)
                return self._format_tool_result(tool_name, tool_result, query)
            else:
                # Trả lời trực tiếp bằng LLM
                messages = [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=query)
                ]
                
                if context:
                    context_msg = f"Thông tin người dùng: {context}"
                    messages.insert(1, SystemMessage(content=context_msg))
                
                response = self.llm.invoke(messages)
                return response.content
                
        except Exception as e:
            return f"Xin lỗi, tôi gặp chút vấn đề kỹ thuật. Bạn thử hỏi lại nhé! (Lỗi: {str(e)})"

    # Backward compatibility
    def run(self, query: str, user_context: Optional[dict] = None, **kwargs) -> Tuple[str, str]:
        """Compatibility method"""
        response = self.chat(query, user_context)
        interaction_id = f"simple_{hash(query) % 10000}"
        return response, interaction_id
    
    def get_agent(self):
        """Compatibility method for routes that expect get_agent()"""
        return self
    
    async def ainvoke(self, inputs: dict, config: Optional[dict] = None):
        """Async invoke method for compatibility"""
        query = inputs.get("input", "")
        response = self.chat(query)
        return {"output": response}
    
    def suggest_recipe(self, ingredients: List[str], preferences: Optional[dict] = None, **kwargs) -> dict:
        """Compatibility method for recipe suggestion"""
        ingredients_str = ", ".join(ingredients)
        query = f"Tôi có {ingredients_str}, gợi ý món gì?"
        
        if preferences:
            if preferences.get("dietary_restrictions"):
                query += f" Hạn chế: {', '.join(preferences['dietary_restrictions'])}"
            if preferences.get("health_conditions"):
                query += f" Tình trạng sức khỏe: {', '.join(preferences['health_conditions'])}"
        
        response = self.chat(query)
        
        return {
            "recipe_suggestion": response,
            "ingredients": ingredients,
            "preferences": preferences,
            "interaction_id": f"recipe_{hash(query) % 10000}"
        }