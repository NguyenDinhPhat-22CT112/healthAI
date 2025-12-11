"""
Authentication Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.connection import get_db
from app.database.models import User, HealthProfile
from app.schemas.user import (
    UserRegister, UserLogin, Token, UserProfile, 
    UserUpdate, HealthProfileCreate, HealthProfileResponse
)
from app.auth.hashing import get_password_hash, verify_password
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Đăng ký tài khoản mới"""
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create empty health profile
    health_profile = HealthProfile(user_id=user.id)
    db.add(health_profile)
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        user_id=user.id,
        username=user.username
    )


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Đăng nhập"""
    
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        user_id=user.id,
        username=user.username
    )


@router.get("/me", response_model=UserProfile)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Lấy thông tin user hiện tại"""
    return current_user


@router.put("/me", response_model=UserProfile)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin user"""
    
    # Update fields
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/health-profile", response_model=HealthProfileResponse)
def get_health_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lấy hồ sơ sức khỏe"""
    
    health_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not health_profile:
        # Create if not exists
        health_profile = HealthProfile(user_id=current_user.id)
        db.add(health_profile)
        db.commit()
        db.refresh(health_profile)
    
    return health_profile


@router.put("/health-profile", response_model=HealthProfileResponse)
def update_health_profile(
    profile_data: HealthProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cập nhật hồ sơ sức khỏe"""
    
    health_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not health_profile:
        health_profile = HealthProfile(user_id=current_user.id)
        db.add(health_profile)
    
    # Update fields
    for field, value in profile_data.model_dump().items():
        setattr(health_profile, field, value)
    
    health_profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(health_profile)
    
    return health_profile
