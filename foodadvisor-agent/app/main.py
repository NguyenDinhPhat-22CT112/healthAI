"""
Entry point FastAPI
"""
from fastapi import FastAPI
from app.routes import analyze_meal, calculate_calories, suggest_recipe

app = FastAPI(title="Food Advisor Agent", version="1.0.0")

# Include routers
app.include_router(analyze_meal.router)
app.include_router(calculate_calories.router)
app.include_router(suggest_recipe.router)


@app.get("/")
async def root():
    return {"message": "Food Advisor Agent API"}

