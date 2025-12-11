"""
Authentication Routes - Login, Register, Profile
"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User, HealthProfile
from app.auth.schemas import (
    UserCreate, UserResponse, UserLogin, Token, 
    UserProfile, HealthProfileCreate, HealthProfileResponse
)
from app.auth.hashing import verify_password, get_password_hash
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_active_user
from app.auth.utils import get_user_by_email, create_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Đăng ký tài khoản mới"""
    
    # Kiểm tra email đã tồn tại
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    
    # Tạo user mới
    user = create_user(db, user_data)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Đăng nhập"""
    
    # Tìm user theo email hoặc username
    user = get_user_by_email(db, form_data.username)
    if not user:
        # Thử tìm theo username
        user = db.query(User).filter(User.username == form_data.username).first()
    
    # Kiểm tra user và password
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/username hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã bị vô hiệu hóa"
        )
    
    # Tạo access token
    access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    # Cập nhật last_login
    user.last_login = user.created_at.__class__.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
    }


@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    """Lấy thông tin profile người dùng hiện tại"""
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        age=current_user.age,
        gender=current_user.gender,
        height=current_user.height,
        weight=current_user.weight,
        activity_level=current_user.activity_level,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.put("/me", response_model=UserProfile)
async def update_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin profile"""
    
    # Cập nhật các field được phép
    allowed_fields = ["full_name", "age", "gender", "height", "weight", "activity_level"]
    
    for field, value in profile_data.items():
        if field in allowed_fields and hasattr(current_user, field):
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        age=current_user.age,
        gender=current_user.gender,
        height=current_user.height,
        weight=current_user.weight,
        activity_level=current_user.activity_level,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/health-profile", response_model=HealthProfileResponse)
async def create_health_profile(
    health_data: HealthProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Tạo hoặc cập nhật hồ sơ sức khỏe"""
    
    # Kiểm tra đã có health profile chưa
    existing_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if existing_profile:
        # Cập nhật existing profile
        for field, value in health_data.dict(exclude_unset=True).items():
            setattr(existing_profile, field, value)
        
        db.commit()
        db.refresh(existing_profile)
        return existing_profile
    else:
        # Tạo mới
        health_profile = HealthProfile(
            user_id=current_user.id,
            **health_data.dict(exclude_unset=True)
        )
        
        db.add(health_profile)
        db.commit()
        db.refresh(health_profile)
        
        return health_profile


@router.get("/health-profile", response_model=Optional[HealthProfileResponse])
async def get_health_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lấy hồ sơ sức khỏe"""
    
    health_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    return health_profile


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Đăng xuất (client sẽ xóa token)"""
    
    return {"message": "Đăng xuất thành công"}