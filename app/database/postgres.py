"""
SQLAlchemy engine, models
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database.models import Base

engine = create_engine(settings.postgres_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import models để SQLAlchemy nhận diện
from app.database.models import (
    User, 
    HealthProfile, 
    MealAnalysis, 
    RecipeQuery, 
    SearchHistory, 
    FoodItem, 
    DiseaseRule
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Khởi tạo database - tạo tất cả bảng"""
    Base.metadata.create_all(bind=engine)

