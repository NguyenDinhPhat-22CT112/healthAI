"""
LangChain ReAct Agent - Food Advisor Agent cho ẩm thực Việt Nam
"""
try:
    # LangChain 1.0+ API
    from langchain_core.tools import BaseTool
    from langchain_core.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain_core.runnables import RunnableLambda
except ImportError:
    # Fallback cho version cũ
    from langchain.tools import BaseTool
    from langchain.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI

from typing import List, Optional
from app.config import settings


class FoodAdvisorAgent:
    """
    ReAct Agent cho tư vấn dinh dưỡng và ẩm thực Việt Nam
    Sử dụng LangChain ReAct framework để kết hợp vision, database query, và recipe generation
    """
    
    def __init__(self, tools: List[BaseTool], model_name: str = "gpt-4", temperature: float = 0.7):
        """
        Khởi tạo Food Advisor Agent
        
        Args:
            tools: Danh sách tools (vision_tool, db_query_tool, recipe_generator_tool)
            model_name: Tên LLM model (gpt-4, gpt-3.5-turbo, etc.)
            temperature: Temperature cho LLM
        """
        self.tools = tools
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=settings.openai_api_key
        )
        self.agent = None
        self.agent_executor = None
        
        # ReAct prompt template cho ẩm thực Việt Nam
        self.react_prompt = PromptTemplate.from_template("""
Bạn là chuyên gia AI về dinh dưỡng và ẩm thực Việt Nam. Bạn am hiểu:
- Các món ăn truyền thống và hiện đại Việt Nam (phở, bún, cơm, gỏi, bánh, canh, etc.)
- Dinh dưỡng phù hợp với khẩu phần người Việt
- Rules dinh dưỡng cho bệnh lý phổ biến tại Việt Nam (tiểu đường, mỡ máu, huyết áp cao, gout)
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
Thought: {agent_scratchpad}
""")
        
    def create_agent(self):
        """
        Tạo simplified agent với tools (không dùng AgentExecutor vì LangChain 1.0 đã thay đổi API)
        """
        if not self.llm:
            raise ValueError("LLM chưa được khởi tạo")
        
        # Bind tools vào LLM
        self.agent = self.llm.bind_tools(self.tools)
        self.agent_executor = self.agent
        
        return self.agent_executor
        
    def run(self, query: str, user_context: Optional[dict] = None) -> str:
        """
        Chạy agent với query
        
        Args:
            query: Câu hỏi/yêu cầu từ người dùng
            user_context: Context về người dùng (bệnh lý, mục tiêu sức khỏe, etc.)
            
        Returns:
            Câu trả lời từ agent
        """
        if not self.agent_executor:
            self.create_agent()
        
        # Thêm user context vào query nếu có
        if user_context:
            context_str = f"\n\nContext người dùng:\n"
            if user_context.get("diseases"):
                context_str += f"- Bệnh lý: {', '.join(user_context['diseases'])}\n"
            if user_context.get("region"):
                context_str += f"- Vùng miền: {user_context['region']}\n"
            if user_context.get("dietary_restrictions"):
                context_str += f"- Hạn chế dinh dưỡng: {', '.join(user_context['dietary_restrictions'])}\n"
            query = query + context_str
        
        try:
            # Sử dụng LLM trực tiếp với tools (simplified approach cho LangChain 1.0)
            if not self.agent_executor:
                self.create_agent()
            
            # Tạo prompt với tools info
            tools_description = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
            full_prompt = f"""
{self.react_prompt.template.format(tools=tools_description, input=query, agent_scratchpad="")}

Câu hỏi: {query}
"""
            
            # Invoke LLM
            response = self.agent_executor.invoke(full_prompt)
            
            # Extract response
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, str):
                return response
            else:
                return str(response)
                
        except Exception as e:
            return f"Lỗi khi chạy agent: {str(e)}. Chi tiết: {type(e).__name__}"
    
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

