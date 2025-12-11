"""
Authentication Schemas - Pydantic models for request/response
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=6, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Mật khẩu phải có ít nhất 6 ký tự')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username chỉ được chứa chữ cái và số')
        return v.lower()


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str  # Có thể là email hoặc username
    password: str


class UserResponse(UserBase):
    """Schema for user response (không có password)"""
    id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Schema for detailed user profile"""
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None  # cm
    weight: Optional[float] = None  # kg
    activity_level: Optional[str] = None
    last_login: Optional[datetime] = None


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[str] = None


class HealthProfileBase(BaseModel):
    """Base health profile schema"""
    diseases: Optional[List[str]] = Field(default_factory=list)
    allergies: Optional[List[str]] = Field(default_factory=list)
    dietary_restrictions: Optional[List[str]] = Field(default_factory=list)
    health_goals: Optional[List[str]] = Field(default_factory=list)
    target_weight: Optional[float] = None
    daily_calorie_target: Optional[int] = None
    doctor_notes: Optional[str] = None
    medications: Optional[List[str]] = Field(default_factory=list)


class HealthProfileCreate(HealthProfileBase):
    """Schema for creating health profile"""
    pass


class HealthProfileResponse(HealthProfileBase):
    """Schema for health profile response"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('Mật khẩu mới phải có ít nhất 6 ký tự')
        return v


class EmailVerification(BaseModel):
    """Schema for email verification"""
    email: EmailStr
    verification_code: str


class PasswordReset(BaseModel):
    """Schema for password reset"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    email: EmailStr
    reset_code: str
    new_password: str = Field(..., min_length=6, max_length=100)


class UserStats(BaseModel):
    """Schema for user statistics"""
    total_meal_analyses: int = 0
    total_recipe_queries: int = 0
    total_interactions: int = 0
    last_activity: Optional[datetime] = None
    favorite_cuisines: List[str] = Field(default_factory=list)
    health_score: Optional[float] = None


class UserPreferences(BaseModel):
    """Schema for user preferences"""
    preferred_language: str = "vi"
    preferred_region: Optional[str] = None  # Bắc, Trung, Nam
    notification_enabled: bool = True
    theme: str = "light"  # light, dark
    measurement_unit: str = "metric"  # metric, imperial


class AuthResponse(BaseModel):
    """Generic auth response"""
    success: bool
    message: str
    data: Optional[dict] = None


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Schema for refresh token response"""
    access_token: str
    token_type: str = "bearer"