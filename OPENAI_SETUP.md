# 🔑 OpenAI API Key Setup Guide

## 📋 **Trạng thái hiện tại**

### ✅ **Hoạt động KHÔNG cần OpenAI:**
- **Health Advisor Tool** - Sử dụng PostgreSQL database
- **Food Analysis** - 271 món ăn Việt Nam từ database
- **Disease Advice** - Quy tắc dinh dưỡng hardcoded
- **Basic Chat** - Trả lời dựa trên tools

### ❌ **Cần OpenAI để hoạt động đầy đủ:**
- **Recipe Generation** - Tạo công thức từ nguyên liệu
- **Natural Conversation** - Trò chuyện tự nhiên với LLM
- **Complex Reasoning** - Phân tích phức tạp

---

## 🚀 **Cách cấu hình OpenAI API Key**

### **Bước 1: Lấy API Key**
1. Truy cập: https://platform.openai.com/api-keys
2. Đăng nhập hoặc tạo tài khoản OpenAI
3. Click **"Create new secret key"**
4. Copy key (dạng: `sk-...`)

### **Bước 2: Cấu hình trong dự án**
```bash
# Mở file .env
nano foodadvisor-agent/.env

# Thay đổi dòng này:
OPENAI_API_KEY=your_openai_api_key_here

# Thành:
OPENAI_API_KEY=sk-your-actual-key-here
```

### **Bước 3: Restart ứng dụng**
```bash
# Restart backend
cd foodadvisor-agent
python app/main.py

# Restart chat
python chat_scripts/chat_agent.py
```

---

## 💰 **Chi phí OpenAI**

### **Free Tier:**
- **$5 credit** khi đăng ký mới
- **Đủ dùng** cho development và testing
- **Hết hạn** sau 3 tháng

### **Pay-as-you-go:**
- **GPT-4o**: ~$0.005/1K tokens
- **Ước tính**: ~$0.01-0.05 per conversation
- **Rất rẻ** cho personal use

---

## 🧪 **Test OpenAI Key**

### **Test nhanh:**
```bash
cd foodadvisor-agent
python -c "
from app.config import settings
print('Key configured:', len(settings.openai_api_key) > 20)
"
```

### **Test đầy đủ:**
```bash
# Chat với agent
python chat_scripts/chat_agent.py

# Hỏi: "Tôi có thịt heo và rau muống, làm món gì?"
# Nếu có OpenAI key → Sẽ tạo công thức chi tiết
# Nếu không có → Sẽ báo lỗi kỹ thuật
```

---

## 🔄 **Alternatives (không cần OpenAI)**

### **1. Chỉ dùng Health Advisor:**
```python
from app.tools.health_advisor import HealthAdvisorTool

tool = HealthAdvisorTool()
result = tool._run(disease="tiểu đường", food_name="phở")
print(result)  # JSON response với lời khuyên
```

### **2. Dùng Google Gemini (miễn phí):**
```bash
# Lấy key từ: https://aistudio.google.com/app/apikey
# Thêm vào .env:
GOOGLE_API_KEY=your-google-key

# Sử dụng Gemini thay vì OpenAI (cần code thêm)
```

### **3. Offline mode:**
- Agent vẫn hoạt động với database
- Trả lời dựa trên tools và hardcoded rules
- Không có conversation tự nhiên

---

## 🎯 **Khuyến nghị**

### **Cho Development:**
- **Dùng OpenAI free tier** - $5 credit đủ dùng lâu
- **Test đầy đủ tính năng** - Recipe generation, natural chat
- **Chi phí thấp** - ~$1-2 cho cả project

### **Cho Production:**
- **Cần OpenAI key** để user experience tốt
- **Monitor usage** để kiểm soát chi phí
- **Có fallback** khi hết quota

### **Cho Demo:**
- **Không cần OpenAI** - Health Advisor vẫn hoạt động tốt
- **Showcase database** - 271 món ăn Việt Nam
- **Disease advice** - Tư vấn chính xác từ PostgreSQL

---

## ❓ **FAQ**

### **Q: Agent có hoạt động không có OpenAI key không?**
A: Có! Health Advisor Tool sử dụng PostgreSQL database, vẫn tư vấn chính xác cho tiểu đường, béo phì, huyết áp cao.

### **Q: Tại sao cần OpenAI?**
A: Để tạo công thức nấu ăn từ nguyên liệu và trò chuyện tự nhiên như Huấn luyện viên Minh Anh.

### **Q: Có alternative nào khác không?**
A: Có thể dùng Google Gemini (miễn phí) hoặc local LLM, nhưng cần code thêm.

### **Q: Chi phí bao nhiêu?**
A: ~$0.01-0.05 per conversation. Free tier $5 đủ dùng vài tháng development.

---

**🎉 Kết luận: Agent hoạt động tốt mà không cần OpenAI, nhưng có OpenAI sẽ đầy đủ tính năng hơn!**