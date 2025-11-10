"""
Script chạy FastAPI server
Đảm bảo chạy từ đúng thư mục
"""
import uvicorn
import sys
from pathlib import Path

# Đảm bảo đang ở đúng thư mục
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    print("\n" + "🚀"*25)
    print("Starting FastAPI Server")
    print("🚀"*25)
    print(f"\n📁 Working directory: {current_dir}")
    print("📋 Server: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("\n💡 Press CTRL+C to stop\n")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(current_dir / "app")],
        log_level="info"
    )

