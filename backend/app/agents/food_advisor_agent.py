"""
LangChain ReAct Agent - Food Advisor Agent cho ẩm thực Việt Nam
"""
    # LangChain 1.0+ API
from langchain_core.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.runnables import RunnableLambda

from app.tools.vision_tool import vision_tool_structured as vision_tool
from app.tools.db_query_tool import db_query_tool_structured as db_query_tool
from app.tools.recipe_generator_tool import recipe_generator_tool_structured as recipe_generator_tool  

from typing import List, Optional
from app.config import settings


class FoodAdvisorAgent:
    """
    ReAct Agent cho tư vấn dinh dưỡng và ẩm thực Việt Nam
    Sử dụng LangChain ReAct framework để kết hợp vision, database query, và recipe generation
    """
    
    def __init__(self, tools: List[BaseTool], model_name: str = "gpt-4o", temperature: float = 0.3):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=settings.openai_api_key
        )

        self.tools = [
            vision_tool,
            db_query_tool,
            recipe_generator_tool
        ]
        
        # ReAct prompt template cho ẩm thực Việt Nam
        self.react_prompt = PromptTemplate.from_template("""
Bạn là chuyên gia AI về dinh dưỡng và ẩm thực Việt Nam. Bạn am hiểu:
- Các món ăn truyền thống và hiện đại Việt Nam (phở, bún, cơm, gỏi, bánh, canh, etc.)
- Dinh dưỡng phù hợp với khẩu phần người Việt
- Rules dinh dưỡng cho bệnh lý phổ biến tại Việt Nam (tiểu đường, mỡ máu, huyết áp cao)
- Văn hóa ẩm thực theo vùng miền (Bắc, Trung, Nam)

Nhiệm vụ của bạn:
1. Phân tích hình ảnh món ăn Việt để nhận diện thành phần và ước tính dinh dưỡng
2. Đưa ra lời khuyên dinh dưỡng phù hợp với thể trạng và bệnh lý người dùng Việt
3. Đề xuất công thức món ăn Việt Nam dựa trên nguyên liệu có sẵn

Sử dụng các tools sau khi cần:
- vision_tool: Nhận diện món ăn Việt Nam từ ảnh
- db_query_tool: Truy vấn thông tin dinh dưỡng và rules bệnh lý
- recipe_generator_tool: Tạo công thức món ăn Việt Nam

Luôn trả lời bằng tiếng Việt, chuyên nghiệp, và tập trung vào ẩm thực Việt Nam.

Tool:
{tools}

Use the following format:

Question: Câu hỏi đầu vào
Thought: Bạn cần suy nghĩ về việc cần làm gì
Action: Tool name để sử dụng
Action Input: Input cho tool
Observation: Kết quả từ tool
... (có thể lặp lại Thought/Action/Action Input/Observation)
Thought: Tôi đã có đủ thông tin để trả lời
Final Answer: Câu trả lời cuối cùng bằng tiếng Việt

Begin!

Question: {input}
{agent_scratchpad}
""")
        
    def create_agent(self):
# Đây mới là cách tạo ReAct agent đúng
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.react_prompt,
        # LangChain sẽ tự inject {tools} và {agent_scratchpad}
        )
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,                    # in ra quá trình Thought/Action để debug
            handle_parsing_errors=True,      # rất quan trọng với tiếng Việt
            max_iterations=10,
            early_stopping_method="generate"  # hoặc "force"
        )
        return self.agent_executor  
        
    def run(self, query: str, user_context: Optional[dict] = None) -> str:
        if not self.agent_executor:
            self.create_agent()

        # Gộp context người dùng (rất quan trọng)
        full_query = query
        if user_context:
            lines = ["=== THÔNG TIN NGƯỜI DÙNG ==="]
            if user_context.get("diseases"):
                lines.append(f"Bệnh lý: {', '.join(user_context['diseases'])}")
            if user_context.get("age"):
                lines.append(f"Tuổi: {user_context['age']}")
            if user_context.get("gender"):
                lines.append(f"Giới tính: {user_context['gender']}")
            if user_context.get("region"):
                lines.append(f"Ưu tiên món vùng: {user_context['region']}")
            if user_context.get("dietary_restrictions"):
                lines.append(f"Hạn chế: {', '.join(user_context['dietary_restrictions'])}")
            full_query = "\n".join(lines) + "\n\n" + query

        try:
            result = self.agent_executor.invoke({
                "input": full_query   # ĐÚNG FORMAT
            })
            return result["output"]   # ĐÚNG KEY
        except Exception as e:
            return f"Agent lỗi: {str(e)}"
    
    def analyze_meal_image(self, image_path: str, user_profile: Optional[dict] = None) -> dict:
        """
        Phân tích bữa ăn từ ảnh với agent
        
        Args:
            image_path: Đường dẫn đến ảnh bữa ăn
            user_profile: Hồ sơ người dùng
            
        Returns:
            Dict chứa kết quả phân tích
        """
        query = f"Phân tích bữa ăn trong ảnh này: {image_path}. Nhận diện món ăn Việt Nam, tính toán dinh dưỡng, và đưa ra lời khuyên."
        
        if user_profile:
            advice_query = "Dựa trên hồ sơ người dùng, đưa ra lời khuyên dinh dưỡng phù hợp."
            query += " " + advice_query
        
        result = self.run(query, user_profile)
        
        return {
            "analysis": result,
            "image_path": image_path,
            "user_profile": user_profile
        }
    
    def suggest_recipe(self, ingredients: List[str], preferences: Optional[dict] = None) -> dict:
        """
        Đề xuất công thức từ nguyên liệu
        
        Args:
            ingredients: Danh sách nguyên liệu có sẵn
            preferences: Sở thích (region, meal_type, dietary_restrictions)
            
        Returns:
            Dict chứa công thức đề xuất
        """
        ingredients_str = ", ".join(ingredients)
        query = f"Đề xuất công thức món ăn Việt Nam từ nguyên liệu: {ingredients_str}"
        
        if preferences:
            if preferences.get("region"):
                query += f". Vùng miền ưu tiên: {preferences['region']}"
            if preferences.get("meal_type"):
                query += f". Loại bữa: {preferences['meal_type']}"
            if preferences.get("dietary_restrictions"):
                query += f". Hạn chế: {', '.join(preferences['dietary_restrictions'])}"
        
        result = self.run(query, preferences)
        
        return {
            "recipe_suggestion": result,
            "ingredients": ingredients,
            "preferences": preferences
        }
    
    def provide_dietary_advice(self, diseases: List[str], user_profile: Optional[dict] = None) -> str:
        """
        Tư vấn chế độ ăn uống theo bệnh lý
        
        Args:
            diseases: Danh sách bệnh lý (VD: ["Tiểu đường", "Huyết áp cao"])
            user_profile: Hồ sơ người dùng (age, gender, height, weight, region, etc.)
            
        Returns:
            Lời khuyên dinh dưỡng từ agent
        """
        diseases_str = ", ".join(diseases)
        query = f"Tư vấn chế độ ăn uống cho người có bệnh lý: {diseases_str}. "
        query += "Đưa ra lời khuyên cụ thể, phù hợp với ẩm thực Việt Nam, bao gồm: "
        query += "- Món ăn nên ăn và nên tránh "
        query += "- Nguyên tắc dinh dưỡng cần tuân thủ "
        query += "- Lời khuyên thực tế cho bữa ăn hàng ngày"
        
        if user_profile:
            if user_profile.get("region"):
                query += f". Ưu tiên các món ăn vùng miền {user_profile['region']}"
            if user_profile.get("meal_type"):
                query += f". Tập trung vào bữa {user_profile['meal_type']}"
            if user_profile.get("current_diet"):
                current_diet_str = ", ".join(user_profile["current_diet"])
                query += f". Chế độ ăn hiện tại: {current_diet_str}"
        
        result = self.run(query, user_profile)
        return result