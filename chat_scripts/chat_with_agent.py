"""
Chat với Food Advisor Agent trực tiếp trên terminal
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.agents.food_advisor_agent import SimpleFoodAgent as FoodAdvisorAgent
from app.tools.vision_tool import VisionTool
from app.tools.recipe_generator_tool import RecipeGeneratorTool
from app.tools.health_advisor import HealthAdvisorTool


def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("🍜 FOOD ADVISOR AGENT - Vietnamese Cuisine AI Assistant")
    print("=" * 70)
    print("Chuyên gia AI về dinh dưỡng và ẩm thực Việt Nam")
    print("🎯 Optimized: 3 Tools | Clean Architecture | Disease-Aware")
    print()
    print("🛠️  Available Tools:")
    print("  📸 Vision Tool - Nhận diện món ăn từ ảnh")
    print("  🍳 Recipe Generator - Tạo công thức từ nguyên liệu")
    print("  🏥 Health Advisor - Tư vấn sức khỏe & phân tích món ăn")
    print()
    print("💡 Commands: 'help', 'clear', 'exit'")
    print("=" * 70)
    print()


def main():
    """Main chat loop"""
    print_banner()
    
    # Khởi tạo tools
    print("🔧 Đang khởi tạo AI Agent...")
    try:
        vision_tool = VisionTool()
        recipe_tool = RecipeGeneratorTool()
        health_advisor_tool = HealthAdvisorTool()
        
        tools = [vision_tool, recipe_tool, health_advisor_tool]
        agent = FoodAdvisorAgent(tools=tools, temperature=0.7)
        
        print("✅ Agent đã sẵn sàng!\n")
    except Exception as e:
        print(f"❌ Lỗi khởi tạo agent: {e}")
        print("💡 Đảm bảo backend đang chạy và database đã kết nối")
        return
    
    # Chat loop
    conversation_history = []
    
    while True:
        try:
            # Nhận input từ user
            user_input = input("🧑 Bạn: ").strip()
            
            if not user_input:
                continue
            
            # Xử lý commands
            if user_input.lower() in ['exit', 'quit', 'thoát']:
                print("\n👋 Tạm biệt! Hẹn gặp lại!")
                break
            
            if user_input.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                print_banner()
                continue
            
            if user_input.lower() == 'help':
                print("\n📚 Ví dụ câu hỏi:")
                print("  🍳 TẠO CÔNG THỨC:")
                print("    - Tôi có thịt heo và rau muống, gợi ý món gì?")
                print("    - Gợi ý món ăn sáng miền Nam")
                print("  🏥 TƯ VẤN SỨC KHỎE:")
                print("    - Người tiểu đường nên ăn gì?")
                print("    - Phân tích món bánh mì cho người huyết áp cao")
                print("    - Tư vấn sức khỏe cho người béo phì")
                print("  📸 NHẬN DIỆN ẢNH:")
                print("    - Phân tích ảnh bữa ăn này")
                print()
                continue
            
            # Gọi agent
            print("\n🤖 Agent đang suy nghĩ...", end="", flush=True)
            
            try:
                response, interaction_id = agent.run(
                    query=user_input,
                    user_context=None,
                    log_interaction=False  # Tắt logging để nhanh hơn
                )
                
                print("\r" + " " * 30 + "\r", end="")  # Clear "đang suy nghĩ"
                print(f"🤖 Agent: {response}\n")
                
                # Lưu vào history
                conversation_history.append({
                    "user": user_input,
                    "agent": response,
                    "interaction_id": interaction_id
                })
                
            except Exception as e:
                print("\r" + " " * 30 + "\r", end="")
                print(f"❌ Lỗi: {e}\n")
                print("💡 Thử hỏi câu khác hoặc kiểm tra kết nối database\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Tạm biệt!")
            break
        except EOFError:
            print("\n\n👋 Tạm biệt!")
            break


if __name__ == "__main__":
    main()
