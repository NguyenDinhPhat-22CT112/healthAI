# 🚀 Tổng quan về FastAPI

## 📖 Khái niệm

**FastAPI** là một framework web hiện đại, hiệu suất cao để xây dựng API với Python 3.7+ dựa trên type hints chuẩn của Python. Được phát triển bởi Sebastián Ramirez và ra mắt lần đầu vào năm 2018, FastAPI đã nhanh chóng trở thành một trong những framework Python phổ biến nhất cho việc phát triển API RESTful và ứng dụng web.

FastAPI được thiết kế với mục tiêu:
- **Hiệu suất cao**: Ngang bằng với NodeJS và Go
- **Dễ sử dụng**: Cú pháp đơn giản, dễ học
- **Tự động hóa**: Tự động tạo documentation và validation
- **Type Safety**: Sử dụng Python type hints
- **Async/Await**: Hỗ trợ lập trình bất đồng bộ

---

## 🏗️ Cấu trúc của FastAPI

FastAPI có một cấu trúc tổ chức linh hoạt và có thể tùy chỉnh theo nhu cầu dự án. Dưới đây là cấu trúc cơ bản của một ứng dụng FastAPI:

### 📁 **Cấu trúc thư mục chuẩn:**

```
my_fastapi_app/
├── app/                    # Thư mục chính chứa ứng dụng
│   ├── __init__.py        # Khởi tạo package
│   ├── main.py            # Entry point của ứng dụng
│   ├── config.py          # Cấu hình ứng dụng
│   ├── dependencies.py    # Dependencies chung
│   │
│   ├── routers/           # Thư mục chứa các router
│   │   ├── __init__.py
│   │   ├── users.py       # Router cho users
│   │   ├── items.py       # Router cho items
│   │   └── auth.py        # Router cho authentication
│   │
│   ├── models/            # Thư mục chứa các model
│   │   ├── __init__.py
│   │   ├── user.py        # User model
│   │   ├── item.py        # Item model
│   │   └── base.py        # Base model
│   │
│   ├── schemas/           # Thư mục chứa Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py        # User schemas
│   │   ├── item.py        # Item schemas
│   │   └── token.py       # Token schemas
│   │
│   ├── services/          # Thư mục chứa business logic
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── item_service.py
│   │   └── auth_service.py
│   │
│   ├── database/          # Thư mục quản lý database
│   │   ├── __init__.py
│   │   ├── connection.py  # Kết nối database
│   │   ├── models.py      # SQLAlchemy models
│   │   └── migrations/    # Database migrations
│   │
│   ├── utils/             # Thư mục chứa utilities
│   │   ├── __init__.py
│   │   ├── security.py    # Security utilities
│   │   ├── helpers.py     # Helper functions
│   │   └── validators.py  # Custom validators
│   │
│   └── tests/             # Thư mục chứa test cases
│       ├── __init__.py
│       ├── test_main.py
│       ├── test_users.py
│       └── test_auth.py
│
├── static/                # Thư mục chứa file tĩnh
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/             # Thư mục chứa HTML templates
│   ├── base.html
│   └── index.html
│
├── uploads/               # Thư mục chứa file upload
├── logs/                  # Thư mục chứa log files
├── .env                   # Environment variables
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── README.md             # Project documentation
```

---

## 📂 Chi tiết các thành phần

### 🎯 **app/main.py** - Entry Point
```python
from fastapi import FastAPI
from app.routers import users, items, auth
from app.database.connection import engine
from app.models import Base

# Tạo ứng dụng FastAPI
app = FastAPI(
    title="My FastAPI App",
    description="API documentation",
    version="1.0.0"
)

# Tạo database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(items.router, prefix="/items", tags=["items"])

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI"}
```

### 🛣️ **app/routers/** - Định tuyến API
Chứa các router modules, mỗi module quản lý một nhóm endpoint liên quan:
- **users.py**: Quản lý các API liên quan đến người dùng
- **items.py**: Quản lý các API liên quan đến sản phẩm
- **auth.py**: Quản lý authentication và authorization

### 🏛️ **app/models/** - Database Models
Chứa các SQLAlchemy models định nghĩa cấu trúc database:
```python
from sqlalchemy import Column, Integer, String, Boolean
from app.database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
```

### 📋 **app/schemas/** - Pydantic Schemas
Chứa các Pydantic models để validation và serialization:
```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True
```

### 🔧 **app/services/** - Business Logic
Chứa logic nghiệp vụ, tách biệt khỏi API endpoints:
```python
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        db_user = User(**user_data.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
```

### 🗄️ **app/database/** - Database Management
Quản lý kết nối và cấu hình database:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### ⚙️ **app/config.py** - Configuration
Chứa các cấu hình ứng dụng:
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 🔐 **app/utils/** - Utilities
Chứa các hàm tiện ích và helper functions:
- **security.py**: Mã hóa password, tạo JWT token
- **helpers.py**: Các hàm hỗ trợ chung
- **validators.py**: Custom validators

### 🧪 **app/tests/** - Testing
Chứa các test cases sử dụng pytest:
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI"}
```

---

## 🔄 So sánh với ASP.NET

| Thành phần | ASP.NET | FastAPI |
|------------|---------|---------|
| **Entry Point** | Global.asax | main.py |
| **Routing** | Controllers/ | routers/ |
| **Models** | Models/ | models/ + schemas/ |
| **Views** | Views/ | templates/ (optional) |
| **Configuration** | Web.config | config.py + .env |
| **Static Files** | Content/ | static/ |
| **Business Logic** | Services/ | services/ |
| **Database** | Entity Framework | SQLAlchemy |
| **Dependency Injection** | Built-in | dependencies.py |
| **Testing** | MSTest/NUnit | pytest |

---

## ✨ Đặc điểm nổi bật của FastAPI

### 🚀 **Performance**
- Hiệu suất cao nhờ Starlette và Pydantic
- Hỗ trợ async/await native
- Tương đương NodeJS và Go về tốc độ

### 📚 **Automatic Documentation**
- Tự động tạo OpenAPI (Swagger) docs
- Interactive API documentation tại `/docs`
- ReDoc documentation tại `/redoc`

### 🔒 **Type Safety**
- Sử dụng Python type hints
- Automatic validation và serialization
- IDE support với autocomplete

### 🔧 **Modern Python Features**
- Python 3.7+ với type hints
- Async/await support
- Dependency injection system

### 🌐 **Standards-based**
- OpenAPI (Swagger) specification
- JSON Schema
- OAuth2 và JWT support

---

## 🎯 Ưu điểm của cấu trúc FastAPI

### ✅ **Tổ chức rõ ràng**
- Separation of concerns
- Modular architecture
- Easy to maintain và scale

### ✅ **Flexibility**
- Có thể tùy chỉnh cấu trúc theo nhu cầu
- Plugin system với dependencies
- Multiple database support

### ✅ **Developer Experience**
- Auto-completion trong IDE
- Automatic API documentation
- Built-in validation và error handling

### ✅ **Production Ready**
- Built-in security features
- Performance optimization
- Docker support

---

## 🚀 Kết luận

FastAPI cung cấp một cấu trúc linh hoạt và mạnh mẽ để xây dựng API hiện đại. Với việc tận dụng các tính năng mới nhất của Python và các tiêu chuẩn web, FastAPI giúp developers xây dựng ứng dụng nhanh chóng, an toàn và dễ bảo trì.

Cấu trúc modular của FastAPI cho phép:
- **Scalability**: Dễ dàng mở rộng ứng dụng
- **Maintainability**: Code dễ đọc và bảo trì
- **Testability**: Dễ dàng viết và chạy tests
- **Reusability**: Tái sử dụng components

So với ASP.NET, FastAPI mang lại sự đơn giản hóa trong cấu hình và triển khai, đồng thời vẫn đảm bảo hiệu suất và tính năng enterprise-grade.

---

*Tài liệu này được tạo dựa trên kinh nghiệm thực tế với FastAPI và các best practices trong cộng đồng Python.*