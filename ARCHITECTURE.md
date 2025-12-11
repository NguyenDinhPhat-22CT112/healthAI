# 🏗️ Food Advisor - Kiến trúc hệ thống

## 📋 **Tổng quan kiến trúc**

Dự án Food Advisor sử dụng **kiến trúc Microservices** với **Clean Architecture** và **Domain-Driven Design (DDD)**, được thiết kế để xây dựng một hệ thống tư vấn dinh dưỡng AI toàn diện cho người Việt Nam.

---

## 🎯 **Mô hình kiến trúc chính**

### **1. 🏛️ Clean Architecture (Hexagonal Architecture)**
```
┌─────────────────────────────────────────────────────────┐
│                    🌐 Presentation Layer                │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │   📱 Mobile App │  │  🌐 REST API    │              │
│  │  (React Native) │  │   (FastAPI)     │              │
│  └─────────────────┘  └─────────────────┘              │
├─────────────────────────────────────────────────────────┤
│                   🧠 Application Layer                  │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │  🤖 AI Agents   │  │  🔧 Services    │              │
│  │  (LangChain)    │  │  (Business)     │              │
│  └─────────────────┘  └─────────────────┘              │
├─────────────────────────────────────────────────────────┤
│                    🏢 Domain Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │  📊 Models      │  │  🛠️ Tools       │              │
│  │  (Entities)     │  │  (AI Tools)     │              │
│  └─────────────────┘  └─────────────────┘              │
├─────────────────────────────────────────────────────────┤
│                 💾 Infrastructure Layer                 │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │  🗄️ PostgreSQL  │  │  🔑 OpenAI API  │              │
│  │  (Main DB)      │  │  (LLM)          │              │
│  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

### **2. 🔄 Microservices Architecture**
```
┌─────────────────────────────────────────────────────────┐
│                    🌐 API Gateway                       │
│                   (FastAPI Main)                       │
├─────────────────────────────────────────────────────────┤
│  🏥 Health Service │  🍳 Recipe Service │  👤 Auth Service │
│  ┌───────────────┐ │  ┌───────────────┐ │  ┌─────────────┐ │
│  │ Health Advisor│ │  │Recipe Generator│ │  │ JWT Auth    │ │
│  │ Disease Rules │ │  │ Meal Planning │ │  │ User Mgmt   │ │
│  │ Food Analysis │ │  │ Ingredients   │ │  │ Permissions │ │
│  └───────────────┘ │  └───────────────┘ │  └─────────────┘ │
├─────────────────────────────────────────────────────────┤
│                   🗄️ Data Layer                         │
│  ┌───────────────┐    ┌───────────────┐                │
│  │  PostgreSQL   │    │  File Storage │                │
│  │  (Structured) │    │  (Images/Data)│                │
│  └───────────────┘    └───────────────┘                │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 **Cấu trúc thư mục theo Domain**

### **🎯 Backend (FastAPI)**
```
app/
├── 🤖 agents/              # AI Agent Layer
│   └── food_advisor_agent.py   # Huấn luyện viên Minh Anh
├── 🛠️ tools/               # Domain Tools
│   ├── health_advisor.py       # Tư vấn sức khỏe
│   ├── recipe_generator_tool.py # Tạo công thức
│   └── db_query_tool.py        # Truy vấn database
├── 🌐 routes/              # API Endpoints
│   ├── auth.py                 # Authentication
│   ├── chat.py                 # AI Chat
│   └── calculate_calories.py   # Nutrition API
├── 🗄️ database/            # Data Access Layer
│   ├── models.py               # SQLAlchemy Models
│   └── connection.py           # DB Connection
├── 🔐 auth/                # Security Layer
│   ├── jwt.py                  # JWT Handling
│   └── utils.py                # Auth Utilities
├── 📊 schemas/             # Data Transfer Objects
├── 🔧 services/            # Business Logic
├── ⚙️ utils/               # Shared Utilities
└── 📝 config.py            # Configuration
```

### **📱 Mobile (React Native)**
```
mobile-app/
├── 📱 app/                 # Expo Router Pages
│   ├── (tabs)/                 # Tab Navigation
│   └── auth/                   # Auth Screens
├── 🎨 src/                 # Source Code
│   ├── components/             # UI Components
│   ├── services/               # API Services
│   └── contexts/               # State Management
├── 🖼️ assets/              # Static Assets
└── ⚙️ contexts/            # Global State
```

---

## 🔄 **Data Flow Architecture**

### **📊 Request Flow:**
```
📱 Mobile App
    ↓ HTTP Request
🌐 FastAPI Router
    ↓ Route Handler
🤖 AI Agent (SimpleFoodAgent)
    ↓ Tool Selection
🛠️ Health Advisor Tool
    ↓ Database Query
🗄️ PostgreSQL Database
    ↓ Data Response
📊 Formatted Response
    ↓ JSON API
📱 Mobile App UI
```

### **🧠 AI Processing Flow:**
```
👤 User Query
    ↓
🤖 SimpleFoodAgent
    ├─ 🔍 Query Analysis
    ├─ 🛠️ Tool Selection
    │   ├─ Health Advisor (Disease + Food)
    │   ├─ Recipe Generator (Ingredients)
    │   └─ Vision Tool (Image Analysis)
    ├─ 🗄️ Database Lookup
    ├─ 🧮 Rule Processing
    └─ 📝 Natural Response Generation
    ↓
💬 Formatted Answer (Huấn luyện viên Minh Anh style)
```

---

## 🏗️ **Design Patterns sử dụng**

### **1. 🎯 Repository Pattern**
```python
# Database abstraction
class DatabaseHelpers:
    @staticmethod
    def get_food_nutrition(food_name: str) -> Optional[Dict]
    
    @staticmethod
    def get_disease_rules(disease_name: str) -> Optional[Dict]
```

### **2. 🏭 Factory Pattern**
```python
# Tool creation
class ToolFactory:
    def create_health_advisor() -> HealthAdvisorTool
    def create_recipe_generator() -> RecipeGeneratorTool
```

### **3. 🎭 Strategy Pattern**
```python
# Different response strategies
class SimpleFoodAgent:
    def _should_use_tool(self, query: str) -> Tuple[str, dict]
    def _format_health_advice(self, data: dict) -> str
    def _format_recipe(self, data: dict) -> str
```

### **4. 🔌 Dependency Injection**
```python
# FastAPI dependencies
def get_db() -> Session:
    # Database session injection

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # User injection
```

---

## 🗄️ **Database Architecture**

### **📊 PostgreSQL Schema Design:**
```
┌─────────────────────────────────────────────────────────┐
│                    👤 User Domain                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │    users    │  │health_profiles│ │nutrition_goals│   │
│  │    auth     │  │   metrics   │  │   targets   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│                   🏥 Health Domain                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │medical_cond │  │  allergies  │  │ medications │     │
│  │disease_rules│  │user_allergies│ │health_logs  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│                   🍽️ Food Domain                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │    foods    │  │food_nutrients│ │    meals    │     │
│  │  nutrition  │  │   details   │  │ meal_foods  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│                  🍳 Recipe Domain                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   recipes   │  │recipe_ingred│ │recipe_ratings│     │
│  │ meal_plans  │  │ ingredients │  │   reviews   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 🤖 **AI Architecture**

### **🧠 Agent-Based Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│                🤖 SimpleFoodAgent                       │
│                (Huấn luyện viên Minh Anh)              │
├─────────────────────────────────────────────────────────┤
│  🛠️ Tool Ecosystem:                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │Health Advisor│ │Recipe Generator│ │Vision Tool  │   │
│  │Disease+Food │  │Ingredients→Recipe│ │Image→Food │   │
│  │PostgreSQL   │  │OpenAI GPT-4 │  │OpenAI Vision│     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│  🧮 Processing Pipeline:                                │
│  Query → Analysis → Tool Selection → Execution →       │
│  Database Lookup → Rule Processing → Response Format   │
└─────────────────────────────────────────────────────────┘
```

### **💬 Conversation Flow:**
```
User Input
    ↓
🔍 Intent Recognition
    ├─ Health Query (disease + food)
    ├─ Recipe Query (ingredients)
    └─ General Chat
    ↓
🛠️ Tool Orchestration
    ├─ Single Tool (specific query)
    ├─ Multiple Tools (complex query)
    └─ Direct Response (simple chat)
    ↓
📝 Response Formatting
    ├─ Huấn luyện viên Minh Anh style
    ├─ Medical disclaimer
    └─ Encouraging follow-up
```

---

## 🔐 **Security Architecture**

### **🛡️ Multi-Layer Security:**
```
┌─────────────────────────────────────────────────────────┐
│  🌐 API Layer Security                                  │
│  ├─ CORS Configuration                                  │
│  ├─ Rate Limiting                                       │
│  └─ Input Validation (Pydantic)                        │
├─────────────────────────────────────────────────────────┤
│  🔑 Authentication Layer                                │
│  ├─ JWT Token-based Auth                               │
│  ├─ Password Hashing (Bcrypt)                          │
│  └─ Secure Session Management                          │
├─────────────────────────────────────────────────────────┤
│  🗄️ Database Security                                   │
│  ├─ SQL Injection Prevention (SQLAlchemy ORM)          │
│  ├─ Connection Pooling                                  │
│  └─ Environment Variable Protection                     │
├─────────────────────────────────────────────────────────┤
│  📱 Mobile Security                                     │
│  ├─ Expo Secure Store                                  │
│  ├─ HTTPS Communication                                │
│  └─ Token Refresh Mechanism                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 **Deployment Architecture**

### **🐳 Containerization:**
```
┌─────────────────────────────────────────────────────────┐
│                   🐳 Docker Compose                    │
├─────────────────────────────────────────────────────────┤
│  📦 Backend Container                                   │
│  ├─ FastAPI Application                                │
│  ├─ Python Dependencies                                │
│  └─ Environment Configuration                          │
├─────────────────────────────────────────────────────────┤
│  🗄️ Database Container                                  │
│  ├─ PostgreSQL 15+                                     │
│  ├─ Data Persistence                                   │
│  └─ Backup Configuration                               │
├─────────────────────────────────────────────────────────┤
│  📱 Mobile Deployment                                   │
│  ├─ Expo Build Service                                 │
│  ├─ App Store / Google Play                           │
│  └─ OTA Updates                                        │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 **Performance Architecture**

### **⚡ Optimization Strategies:**
```
🔄 Caching Layer:
├─ Database Query Caching
├─ API Response Caching
└─ Static Asset Caching

🗄️ Database Optimization:
├─ Indexes on frequent queries
├─ Connection pooling
└─ Query optimization

🤖 AI Optimization:
├─ Tool selection logic
├─ Response caching
└─ Fallback mechanisms

📱 Mobile Optimization:
├─ Lazy loading
├─ Image optimization
└─ Bundle splitting
```

---

## 🎯 **Architectural Benefits**

### ✅ **Scalability:**
- Microservices can scale independently
- Database sharding ready
- Horizontal scaling support

### ✅ **Maintainability:**
- Clean separation of concerns
- Domain-driven design
- Modular architecture

### ✅ **Testability:**
- Dependency injection
- Mock-friendly design
- Unit test isolation

### ✅ **Flexibility:**
- Plugin architecture for tools
- Multiple AI model support
- Database agnostic design

### ✅ **Security:**
- Multi-layer security
- JWT-based authentication
- Input validation

---

## 🔮 **Future Architecture Evolution**

### **📈 Planned Enhancements:**
```
🌐 Microservices Expansion:
├─ Notification Service
├─ Analytics Service
└─ ML Training Service

🤖 AI Enhancement:
├─ Multi-model support (Gemini, Claude)
├─ Local LLM integration
└─ Custom model training

📊 Data Architecture:
├─ Data lake for analytics
├─ Real-time streaming
└─ ML pipeline integration

🔄 DevOps:
├─ CI/CD pipeline
├─ Monitoring & logging
└─ Auto-scaling
```

---

## 📋 **Architecture Summary**

**🏗️ Kiến trúc chính:** Clean Architecture + Microservices + Domain-Driven Design

**🎯 Đặc điểm nổi bật:**
- **Modular**: Tách biệt rõ ràng các domain
- **Scalable**: Có thể mở rộng từng service
- **Maintainable**: Dễ bảo trì và phát triển
- **Secure**: Bảo mật multi-layer
- **AI-First**: Thiết kế xoay quanh AI agent

**🚀 Công nghệ core:**
- **Backend**: FastAPI + PostgreSQL + LangChain
- **Mobile**: React Native + Expo SDK 54
- **AI**: OpenAI GPT-4 + Custom Tools
- **DevOps**: Docker + Environment Config

**🎉 Kết quả:** Một hệ thống tư vấn dinh dưỡng AI hoàn chỉnh, có thể mở rộng và bảo trì dễ dàng!**