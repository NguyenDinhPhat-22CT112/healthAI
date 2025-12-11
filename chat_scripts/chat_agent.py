"""
Chat với Simple Food Agent - Không dùng Vision Tool
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.agents.food_advisor_agent import SimpleFoodAgent
from app.tools.recipe_generator_tool import RecipeGeneratorTool
from app.tools.health_advisor import HealthAdvisorTool


def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("🍜 SIMPLE FOOD ADVISOR - Trò chuyện tự nhiên")
    print("=" * 70)
    print("Huấn luyện viên Sức khỏe Minh Anh - Chuyên gia dinh dưỡng & ẩm thực Việt Nam")
    print("💬 Trả lời tự nhiên, thân thiện như bác sĩ gia đình")
    print()
    print("🎯 Hỏi tôi về:")
    print("  🏥 Tư vấn sức khỏe: tiểu đường, béo phì, huyết áp cao")
    print("  🍳 Công thức nấu ăn: từ nguyên liệu có sẵn")
    print("  📊 Phân tích món ăn: dinh dưỡng, phù hợp với bệnh lý")
    print("  🥘 Ẩm thực Việt: 3 miền Bắc - Trung - Nam")
    print()
    print("💡 Commands: 'help', 'clear', 'exit'")
    print("=" * 70)
    print()


def main():
    """Main chat loop"""
    print_banner()
    
    # Khởi tạo tools và agent (không có vision)
    print("🔧 Đang khởi tạo Bác sĩ Lan...")
    try:
        recipe_tool = RecipeGeneratorTool()
        health_advisor_tool = HealthAdvisorTool()
        
        tools = [recipe_tool, health_advisor_tool]
        agent = SimpleFoodAgent(tools=tools, temperature=0.7)
        
        print("✅ Huấn luyện viên Minh Anh đã sẵn sàng tư vấn!\n")
    except Exception as e:
        print(f"❌ Lỗi khởi tạo: {e}")
        print("💡 Đảm bảo backend đang chạy và có kết nối internet")
        return
    
    # Chat loop
    print("👋 Chào bạn! Tôi là Huấn luyện viên Sức khỏe Minh Anh. Hôm nay bạn cần tư vấn gì về dinh dưỡng?")
    print()
    
    while True:
        try:
            # Nhận input từ user
            user_input = input("🧑 Bạn: ").strip()
            
            if not user_input:
                continue
            
            # Xử lý commands
            if user_input.lower() in ['exit', 'quit', 'thoát', 'bye']:
                print("\n👋 Chúc bạn sức khỏe! Hẹn gặp lại!")
                break
            
            if user_input.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                print_banner()
                print("👋 Chào bạn! Tôi là Huấn luyện viên Sức khỏe Minh Anh. Hôm nay bạn cần tư vấn gì về dinh dưỡng?")
                print()
                continue
            
            if user_input.lower() == 'help':
                print("\n📚 Ví dụ câu hỏi tự nhiên:")
                print("  🏥 TƯ VẤN SỨC KHỎE:")
                print("    - Người tiểu đường ăn phở được không?")
                print("    - Tôi bị huyết áp cao, nên ăn gì?")
                print("    - Béo phì có nên ăn cơm tấm không?")
                print("  🍳 CÔNG THỨC NẤU ĂN:")
                print("    - Tôi có thịt heo và rau muống, làm món gì?")
                print("    - Cách nấu bún bò Huế")
                print("    - Gợi ý món ăn sáng miền Nam")
                print("  💬 TRUYỆN TRỜI:")
                print("    - Món nào ngon nhất Việt Nam?")
                print("    - Sự khác biệt ẩm thực 3 miền?")
                print("    - Tại sao phở lại nổi tiếng?")
                print()
                continue
            
            # Chat với agent
            print("🤖 ", end="", flush=True)
            
            try:
                response = agent.chat(user_input)
                print(f"Minh Anh: {response}\n")
                
            except Exception as e:
                print(f"Xin lỗi, tôi gặp chút vấn đề kỹ thuật: {e}")
                print("Bạn thử hỏi lại câu khác nhé! 😊\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Chúc bạn sức khỏe!")
            break
        except EOFError:
            print("\n\n👋 Chúc bạn sức khỏe!")
            break


if __name__ == "__main__":
    main()