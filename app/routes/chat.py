"""
Chat API - Tư vấn dinh dưỡng với AI
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.database.postgres import get_db
from app.auth.dependencies import get_current_active_user
from app.database.models import User
from app.agents.food_advisor_agent import SimpleFoodAgent as FoodAdvisorAgent
from app.tools.health_advisor_simple import HealthAdvisorTool
from app.tools.recipe_generator_tool import RecipeGeneratorTool
from app.tools.db_query_tool import DBQueryTool
import json

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    """Chat message request"""
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response"""
    message: str
    type: str = "text"  # text, suggestion, warning
    suggestions: Optional[List[str]] = None
    data: Optional[Dict[str, Any]] = None


@router.post("/", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Chat với AI tư vấn dinh dưỡng
    """
    try:
        # Initialize tools
        health_tool = HealthAdvisorTool()
        recipe_tool = RecipeGeneratorTool()
        db_tool = DBQueryTool()
        
        # Initialize agent with tools
        agent = FoodAdvisorAgent(
            tools=[health_tool, recipe_tool, db_tool],
            model_name="gpt-4o",
            temperature=0.7
        )
        
        # Prepare context with user health info
        user_context = {
            "user_id": current_user.id,
            "user_name": current_user.full_name or current_user.email,
        }
        
        # Add health profile if available
        if hasattr(current_user, 'health_profile') and current_user.health_profile:
            health_profile = current_user.health_profile
            user_context.update({
                "medical_conditions": getattr(health_profile, 'medical_conditions', []),
                "allergies": getattr(health_profile, 'allergies', []),
                "dietary_restrictions": getattr(health_profile, 'dietary_restrictions', []),
                "age": getattr(health_profile, 'age', None),
                "gender": getattr(health_profile, 'gender', None),
                "weight": getattr(health_profile, 'weight', None),
                "height": getattr(health_profile, 'height', None),
            })
        
        # Merge with provided context
        if chat_request.context:
            user_context.update(chat_request.context)
        
        # Create enhanced prompt with context
        enhanced_message = f"""
        Người dùng: {user_context.get('user_name', 'Khách')}
        Thông tin sức khỏe: {json.dumps(user_context, ensure_ascii=False, indent=2)}
        
        Câu hỏi: {chat_request.message}
        
        Hãy trả lời bằng tiếng Việt, tư vấn dinh dưỡng phù hợp với tình trạng sức khỏe của người dùng.
        """
        
        # Get response from agent
        session_id = f"user_{current_user.id}"
        agent_with_history = agent.get_agent()
        
        response = await agent_with_history.ainvoke(
            {"input": enhanced_message},
            config={"configurable": {"session_id": session_id}}
        )
        
        ai_response = response.get("output", "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này.")
        
        # Analyze response to determine type and suggestions
        response_type = "text"
        suggestions = []
        
        # Check for health warnings
        if any(word in ai_response.lower() for word in ["cảnh báo", "nguy hiểm", "tránh", "không nên"]):
            response_type = "warning"
        
        # Generate suggestions based on user context
        if user_context.get('medical_conditions'):
            conditions = user_context['medical_conditions']
            if 'tiểu đường' in str(conditions).lower():
                suggestions.extend([
                    "Thực đơn cho người tiểu đường",
                    "Cách kiểm soát đường huyết",
                    "Thực phẩm có chỉ số đường huyết thấp"
                ])
            if 'cao huyết áp' in str(conditions).lower():
                suggestions.extend([
                    "Chế độ ăn ít muối",
                    "Thực phẩm giảm huyết áp",
                    "Bài tập cho người cao huyết áp"
                ])
        
        # Default suggestions if no specific conditions
        if not suggestions:
            suggestions = [
                "Tính calo món ăn hôm nay",
                "Gợi ý thực đơn tuần này",
                "Thực phẩm tốt cho sức khỏe",
                "Cách nấu ăn dinh dưỡng"
            ]
        
        return ChatResponse(
            message=ai_response,
            type=response_type,
            suggestions=suggestions[:3],  # Limit to 3 suggestions
            data={
                "session_id": session_id,
                "user_context": user_context
            }
        )
        
    except Exception as e:
        # Fallback response
        return ChatResponse(
            message="Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau.",
            type="text",
            suggestions=[
                "Thử lại câu hỏi",
                "Liên hệ hỗ trợ",
                "Xem FAQ"
            ]
        )


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_chat_history(
    current_user: User = Depends(get_current_active_user),
    limit: int = 20
):
    """
    Lấy lịch sử chat của user
    """
    # This would typically come from a database
    # For now, return empty list as we're using in-memory storage
    return []


@router.delete("/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_active_user)
):
    """
    Xóa lịch sử chat của user
    """
    # Clear the session history for this user
    session_id = f"user_{current_user.id}"
    
    # This would clear from the agent's memory store
    # For now, just return success
    return {"message": "Đã xóa lịch sử chat"}