"""
JWT Token Handler - Create, decode, validate JWT tokens
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.config import settings

# JWT Configuration
SECRET_KEY = settings.secret_key or settings.openai_api_key or "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class JWTHandler:
    """JWT Token Handler Class"""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Tạo JWT access token
        
        Args:
            data: Payload data (thường chứa user_id trong 'sub')
            expires_delta: Thời gian hết hạn (optional)
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Thêm thông tin hết hạn và metadata
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),  # issued at
            "type": "access_token"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        Tạo refresh token (thời gian sống lâu hơn)
        
        Args:
            user_id: ID của user
            
        Returns:
            Refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=30)  # 30 days
        
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh_token"
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode và validate JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Payload dict nếu valid, None nếu invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Kiểm tra token type
            token_type = payload.get("type")
            if token_type not in ["access_token", "refresh_token"]:
                return None
            
            # Kiểm tra expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                return None
            
            return payload
            
        except JWTError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[str]:
        """
        Lấy user_id từ token
        
        Args:
            token: JWT token string
            
        Returns:
            User ID nếu token valid, None nếu invalid
        """
        payload = JWTHandler.decode_token(token)
        if payload:
            return payload.get("sub")
        return None
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Kiểm tra token đã hết hạn chưa
        
        Args:
            token: JWT token string
            
        Returns:
            True nếu hết hạn, False nếu còn hiệu lực
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = payload.get("exp")
            
            if exp:
                return datetime.fromtimestamp(exp) < datetime.utcnow()
            
            return True  # Không có exp thì coi như hết hạn
            
        except JWTError:
            return True
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[str]:
        """
        Tạo access token mới từ refresh token
        
        Args:
            refresh_token: Refresh token string
            
        Returns:
            Access token mới nếu refresh token valid, None nếu invalid
        """
        payload = JWTHandler.decode_token(refresh_token)
        
        if not payload:
            return None
        
        # Kiểm tra là refresh token
        if payload.get("type") != "refresh_token":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Tạo access token mới
        new_access_token = JWTHandler.create_access_token(
            data={"sub": user_id}
        )
        
        return new_access_token
    
    @staticmethod
    def validate_token_format(token: str) -> bool:
        """
        Kiểm tra format của token có đúng không
        
        Args:
            token: JWT token string
            
        Returns:
            True nếu format đúng, False nếu sai
        """
        if not token:
            return False
        
        # JWT token có 3 phần cách nhau bởi dấu chấm
        parts = token.split(".")
        return len(parts) == 3


# Convenience functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Wrapper function for backward compatibility"""
    return JWTHandler.create_access_token(data, expires_delta)


def decode_token(token: str) -> Optional[dict]:
    """Wrapper function for backward compatibility"""
    return JWTHandler.decode_token(token)


def get_user_id_from_token(token: str) -> Optional[str]:
    """Wrapper function for backward compatibility"""
    return JWTHandler.get_user_id_from_token(token)