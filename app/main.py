"""
Entry point FastAPI - Complete Food Advisor Agent System
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# Import settings
from app.core.settings import settings

# Import routes
from app.auth import auth_router
from app.routes import (
    meals,
    recipes,
    training,
    foods,
    analyze_meal,
    suggest_recipe,
    calculate_calories,
    chat,
)

# Import database init
from app.database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ------------------- Startup -------------------
    print("🚀 Starting Food Advisor Agent...")
    try:
        init_db()  # Sync function
        print("✅ Database connected & initialized successfully")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
        # Continue anyway - graceful degradation
    
    yield  # <-- App runs here
    
    # ------------------- Shutdown ------------------
    print("🛑 Shutting down Food Advisor Agent...")


# Khởi tạo app với lifespan (modern FastAPI way)
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered Vietnamese cuisine advisor with health-aware meal analysis & personalized recipe suggestions",
    lifespan=lifespan,
)

# ==================== CORS ====================
# Dynamic CORS based on environment
allowed_origins = settings.allowed_origins
if settings.environment == "development":
    allowed_origins = ["*"]  # Allow all in development

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Static Files ====================
UPLOAD_DIR = "uploads/meals"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ==================== Include Routers ====================
# Main API routes (with prefixes for organization)
app.include_router(auth_router, tags=["Authentication"])
app.include_router(meals.router, prefix="/meals", tags=["Meals"])
app.include_router(recipes.router, prefix="/recipes", tags=["Recipe"])
app.include_router(training.router, prefix="/training", tags=["Training & Feedback"])
app.include_router(foods.router, prefix="/api/foods", tags=["Food Database"])
app.include_router(chat.router, tags=["Chat AI"])

# Legacy routes (for backward compatibility)
app.include_router(analyze_meal.router, tags=["Legacy - Meal Analysis"])
app.include_router(suggest_recipe.router, tags=["Legacy - Recipe Suggestion"])
app.include_router(calculate_calories.router, tags=["Legacy - Calorie Calculator"])

# ==================== Root & Health Endpoints ====================
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "features": [
            "🔐 User Authentication & Health Profiles",
            "📸 Meal Photo Analysis (GPT-4 Vision + health context)",
            "🍳 Personalized Recipe Suggestions",
            "🏥 Disease & Allergy Aware AI",
            "📊 Meal History & Statistics",
            "🎓 Training/Feedback Loop",
            "🗄️  Vietnamese Food Database",
            "🧮 Calorie Calculator"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "auth": "/auth",
            "meals": "/meals",
            "recipes": "/recipes",
            "training": "/training",
            "foods": "/api/foods"
        },
        "legacy_endpoints": {
            "analyze_meal": "/analyze-meal/",
            "suggest_recipe": "/suggest-recipe/", 
            "calculate_calories": "/calculate-calories/"
        }
    }


@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "database": {
            "postgresql": "connected" if settings.postgres_url else "not configured",
            "mongodb": "configured" if settings.mongo_url else "not configured"
        },
        "ai_models": {
            "openai": "configured" if settings.openai_api_key else "not configured",
            "google": "configured" if settings.google_api_key else "not configured"
        },
        "features": {
            "authentication": True,
            "meal_analysis": True,
            "recipe_suggestions": True,
            "training_system": True,
            "food_database": True
        }
    }

