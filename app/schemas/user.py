"""
User Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserRegister(BaseModel):
    """User registration"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT Token"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


class UserProfile(BaseModel):
    """User profile response"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    activity_level: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Update user profile"""
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    activity_level: Optional[str] = None


class HealthProfileCreate(BaseModel):
    """Create/Update health profile"""
    diseases: List[str] = []
    allergies: List[str] = []
    dietary_restrictions: List[str] = []
    health_goals: List[str] = []
    target_weight: Optional[float] = None
    daily_calorie_target: Optional[int] = None
    doctor_notes: Optional[str] = None
    medications: List[str] = []


class HealthProfileResponse(BaseModel):
    """Health profile response"""
    id: str
    user_id: str
    diseases: List[str]
    allergies: List[str]
    dietary_restrictions: List[str]
    health_goals: List[str]
    target_weight: Optional[float]
    daily_calorie_target: Optional[int]
    doctor_notes: Optional[str]
    medications: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
