"""
Authentication Module - Complete auth system for Food Advisor
Organized by microservices pattern with clear separation of concerns
"""

# Router
from .router import router as auth_router

# Dependencies (main auth functions)
from .dependencies import (
    AuthDependencies,
    CurrentUser,
    CurrentActiveUser,
    CurrentVerifiedUser,
    OptionalUser,
    CurrentAdmin,
    UserWithHealthProfile,
    UserWithRequiredHealthProfile,
    get_current_user,
    get_current_active_user,
    get_optional_user,
    require_admin,
    verify_token_only
)

# JWT token management
from .jwt import JWTHandler, create_access_token, decode_token

# Password hashing
from .hashing import (
    PasswordHasher,
    password_hasher,
    get_password_hash,
    verify_password,
    generate_random_password,
    validate_password_strength
)

# Utilities
from .utils import (
    get_user_by_email,
    get_user_by_username,
    get_user_by_id,
    create_user,
    is_email_available,
    is_username_available,
    calculate_bmi,
    get_bmi_category,
    calculate_daily_calories,
    get_health_recommendations,
    generate_username,
    update_user_last_login
)

# Schemas
from .schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    UserProfile,
    Token,
    TokenData,
    HealthProfileCreate,
    HealthProfileResponse,
    PasswordChange,
    EmailVerification,
    PasswordReset,
    PasswordResetConfirm,
    UserStats,
    UserPreferences,
    AuthResponse,
    RefreshTokenRequest,
    RefreshTokenResponse
)

__all__ = [
    # Router
    "auth_router",
    
    # Dependencies
    "AuthDependencies",
    "CurrentUser",
    "CurrentActiveUser", 
    "CurrentVerifiedUser",
    "OptionalUser",
    "CurrentAdmin",
    "UserWithHealthProfile",
    "UserWithRequiredHealthProfile",
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "require_admin",
    "verify_token_only",
    
    # JWT
    "JWTHandler",
    "create_access_token",
    "decode_token",
    
    # Hashing
    "PasswordHasher",
    "password_hasher",
    "get_password_hash",
    "verify_password",
    "generate_random_password",
    "validate_password_strength",
    
    # Utils
    "get_user_by_email",
    "get_user_by_username",
    "get_user_by_id",
    "create_user",
    "is_email_available",
    "is_username_available",
    "calculate_bmi",
    "get_bmi_category",
    "calculate_daily_calories",
    "get_health_recommendations",
    "generate_username",
    "update_user_last_login",
    
    # Schemas
    "UserCreate",
    "UserResponse",
    "UserLogin", 
    "UserProfile",
    "Token",
    "TokenData",
    "HealthProfileCreate",
    "HealthProfileResponse",
    "PasswordChange",
    "EmailVerification",
    "PasswordReset",
    "PasswordResetConfirm",
    "UserStats",
    "UserPreferences",
    "AuthResponse",
    "RefreshTokenRequest",
    "RefreshTokenResponse"
]