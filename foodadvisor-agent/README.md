# Health AI – Trợ lý Ẩm thực và Dinh dưỡng Việt Nam

Hệ thống AI tư vấn dinh dưỡng tập trung vào ẩm thực Việt Nam, sử dụng LangChain ReAct Agent, Vision AI, và AI Reasoning.

## Tính năng chính

### 1. Food Image Recognition & Analysis (Ẩm thực Việt)
- Nhận diện món ăn Việt Nam từ ảnh (Phở bò, Cơm tấm, Gỏi cuốn, etc.)
- Phân tích thành phần chính và ước tính khẩu phần
- Hỗ trợ các món ăn theo vùng miền (Bắc, Trung, Nam)

### 2. Nutrition & Calorie Estimation
- Tính toán calo và dinh dưỡng dựa trên khẩu phần thực tế người Việt
- Hỗ trợ nhiều đơn vị (gram, khẩu phần)
- Database Việt hóa với thông tin dinh dưỡng chính xác

### 3. Recipe Suggestion
- Đề xuất công thức món ăn Việt Nam dựa trên nguyên liệu có sẵn
- Gợi ý theo vùng miền, loại bữa, và hạn chế dinh dưỡng
- Hỗ trợ cả món truyền thống và hiện đại

### 4. Health & Dietary Advice
- Tư vấn dinh dưỡng phù hợp với bệnh lý phổ biến tại Việt Nam:
  - Tiểu đường
  - Mỡ máu cao
  - Huyết áp cao
  - Gout
- Merge rules khi người dùng có nhiều bệnh lý
- Lời khuyên cụ thể cho ẩm thực Việt Nam

## Cấu trúc dự án

```
foodadvisor-agent/
├── app/
│   ├── main.py                      # FastAPI entry point
│   ├── config.py                    # Settings (DB URLs, API keys)
│   ├── database/
│   │   ├── postgres.py              # SQLAlchemy engine, models
│   │   ├── models.py                # SQLAlchemy models (User, FoodItem, Recipe, DiseaseRule)
│   │   └── mongo.py                 # PyMongo client
│   ├── models/                       # Pydantic models
│   │   ├── food.py                  # Models cho món ăn Việt Nam
│   │   ├── disease.py               # Models cho rules bệnh lý
│   │   ├── recipe.py                # Models cho công thức
│   │   └── user.py                  # Models cho user profile
│   ├── routes/
│   │   ├── analyze_meal.py          # API: Tư vấn bữa ăn từ ảnh
│   │   ├── calculate_calories.py    # API: Tính calo
│   │   └── suggest_recipe.py        # API: Đề xuất công thức
│   ├── agents/
│   │   └── food_advisor_agent.py    # LangChain ReAct agent
│   ├── tools/
│   │   ├── vision_tool.py           # Tool: Nhận diện ảnh món ăn Việt
│   │   ├── db_query_tool.py         # Tool: Query DB
│   │   └── recipe_generator_tool.py # Tool: Generate recipe
│   └── utils/
│       ├── data_loader.py           # Load Excel vào PostgreSQL
│       └── rules_merger.py          # Merge rules cho bệnh khác
├── data/
│   └── foodData.xlsx                # Dataset dinh dưỡng món ăn Việt
├── images/                           # Folder cho dataset hình ảnh
├── requirements.txt
├── .env
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Hướng dẫn setup

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình environment variables

Tạo file `.env` với nội dung:

#### Option A: Sử dụng MongoDB Atlas (Khuyến nghị)

```env
POSTGRES_URL=postgresql://fooduser:foodpass@localhost:5432/foodadvisor

# MongoDB Atlas Connection String
# Format: mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
MONGO_URL=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/foodadvisor?retryWrites=true&w=majority
MONGO_DB_NAME=foodadvisor

OPENAI_API_KEY=your_openai_api_key_here
```

**Lấy MongoDB Atlas Connection String:**
1. Đăng nhập vào [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Vào **Connect** → **Connect your application**
3. Copy connection string và thay thế `<password>` và `<database>` bằng thông tin của bạn

#### Option B: Sử dụng Local MongoDB

```env
POSTGRES_URL=postgresql://fooduser:foodpass@localhost:5432/foodadvisor
MONGO_URL=mongodb://localhost:27017/
MONGO_DB_NAME=foodadvisor
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Khởi tạo database

```python
from app.database.postgres import init_db
from app.utils.data_loader import init_sample_data

# Tạo tables
init_db()

# Load dữ liệu mẫu (optional)
init_sample_data()
```

### 4. Load dữ liệu từ Excel (nếu có)

```python
from app.utils.data_loader import load_excel_to_postgres

# Load food items
load_excel_to_postgres("data/foodData.xlsx", table_name="food_items")

# Load recipes
load_excel_to_postgres("data/foodData.xlsx", table_name="recipes", sheet_name="recipes")

# Load disease rules
load_excel_to_postgres("data/foodData.xlsx", table_name="disease_rules", sheet_name="disease_rules")
```

### 5. Chạy với Docker Compose

#### Nếu dùng MongoDB Atlas:
```bash
# Set MONGO_URL trong .env với Atlas connection string
# Sau đó chạy (không start MongoDB local service)
docker-compose up -d postgres api
```

#### Nếu dùng Local MongoDB:
```bash
# Start tất cả services bao gồm MongoDB local
docker-compose --profile local-mongo up -d
```

### 6. Chạy local development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API sẽ chạy tại `http://localhost:8000`

## API Endpoints

### 1. Phân tích bữa ăn từ ảnh

```bash
POST /analyze-meal/
Content-Type: multipart/form-data

# Form data:
- image: File (ảnh bữa ăn)
- user_id: string (optional)
- diseases: string (JSON array, optional)
- region: string (Bắc/Trung/Nam, optional)
```

**Ví dụ với curl:**
```bash
curl -X POST "http://localhost:8000/analyze-meal/" \
  -F "image=@images/pho_bo.jpg" \
  -F "diseases=[\"Tiểu đường\"]" \
  -F "region=Bắc"
```

**Response:**
```json
{
  "status": "success",
  "dish_name": "Phở bò",
  "main_ingredients": ["thịt bò", "bánh phở", "hành lá"],
  "estimated_weight_g": 300,
  "nutrition": {
    "calories": 450,
    "protein": 36,
    "fat": 9,
    "carbs": 60
  },
  "health_advice": "Lời khuyên dinh dưỡng..."
}
```

### 2. Tính calo và dinh dưỡng

```bash
POST /calculate-calories/
Content-Type: application/json

{
  "foods": [
    {"name": "Phở bò", "quantity": 1, "unit": "serving"},
    {"name": "Gỏi cuốn", "quantity": 3, "unit": "serving"}
  ]
}
```

### 3. Đề xuất công thức

```bash
POST /suggest-recipe/
Content-Type: application/json

{
  "available_ingredients": ["thịt heo", "trứng", "rau muống"],
  "region_preference": "Nam",
  "meal_type": "tối",
  "dietary_restrictions": ["tiểu đường"],
  "max_calories": 500
}
```

### 4. Lấy danh sách món ăn phổ biến

```bash
GET /suggest-recipe/popular-vietnamese
```

## Ví dụ món ăn Việt Nam

Hệ thống hỗ trợ nhận diện và tư vấn cho các món ăn phổ biến:

1. **Phở bò** (Bắc) - ~450 cal/tô
2. **Bún bò Huế** (Trung) - ~550 cal/tô
3. **Cơm tấm sườn nướng** (Nam) - ~650 cal/phần
4. **Gỏi cuốn** (Nam) - ~60 cal/cuốn
5. **Bánh xèo** (Nam) - ~350 cal/cái

## Database

### PostgreSQL
- **User Profiles**: Thông tin người dùng, bệnh lý, mục tiêu sức khỏe
- **Food Items**: Dữ liệu dinh dưỡng món ăn Việt Nam
- **Recipes**: Công thức món ăn
- **Disease Rules**: Rules dinh dưỡng cho bệnh lý

### MongoDB (Atlas hoặc Local)
- **Meal Logs**: Nhật ký bữa ăn, kết quả phân tích hình ảnh
- **Activity Logs**: Log tương tác của người dùng

**Lưu ý**: Hệ thống hỗ trợ cả MongoDB Atlas (cloud) và MongoDB local. Khuyến nghị sử dụng MongoDB Atlas cho production.

## Documentation

API documentation có sẵn tại:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Technology Stack

- **FastAPI**: Web framework
- **LangChain**: ReAct Agent framework
- **OpenAI**: GPT-4, GPT-4 Vision cho nhận diện và tư vấn
- **PostgreSQL**: Structured data storage
- **MongoDB**: Unstructured data storage
- **SQLAlchemy**: ORM cho PostgreSQL
- **PyMongo**: MongoDB client
- **Pydantic**: Data validation

## Dataset Việt hóa

Hệ thống được thiết kế để:
1. Huấn luyện ban đầu với dataset quốc tế (Food-101, UEC-Food256)
2. Mở rộng với dataset món ăn Việt Nam từ:
   - Cookpad Việt Nam
   - Điện Máy Xanh
   - Món Ngon Mỗi Ngày
3. Học dần từ user interactions để cải thiện độ chính xác

## License

MIT License

