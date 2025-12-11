"""
Authentication Dependencies - FastAPI dependencies for auth
"""
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User, HealthProfile
from app.auth.jwt import JWTHandler
from app.auth.utils import get_user_by_id

# Security schemes
bearer_scheme = HTTPBearer()
optional_bearer_scheme = HTTPBearer(auto_error=False)


class AuthDependencies:
    """
    Authentication dependencies class
    """
    
    @staticmethod
    def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db)
    ) -> User:
        """
        Get current authenticated user from JWT token
        
        Args:
            credentials: HTTP Bearer credentials
            db: Database session
            
        Returns:
            Current user object
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        if not credentials:
            raise credentials_exception
        
        token = credentials.credentials
        
        # Decode token
        payload = JWTHandler.decode_token(token)
        if payload is None:
            raise credentials_exception
        
        # Get user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Get user from database
        user = get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        return user
    
    @staticmethod
    def get_current_active_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Get current active user (additional validation)
        
        Args:
            current_user: Current user from get_current_user
            
        Returns:
            Current active user
            
        Raises:
            HTTPException: If user is not active or verified
        """
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        return current_user
    
    @staticmethod
    def get_current_verified_user(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """
        Get current verified user
        
        Args:
            current_user: Current active user
            
        Returns:
            Current verified user
            
        Raises:
            HTTPException: If user is not verified
        """
        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required"
            )
        
        return current_user
    
    @staticmethod
    def get_optional_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer_scheme),
        db: Session = Depends(get_db)
    ) -> Optional[User]:
        """
        Get current user if token is provided, otherwise return None
        Useful for endpoints that work both with and without authentication
        
        Args:
            credentials: Optional HTTP Bearer credentials
            db: Database session
            
        Returns:
            User object if authenticated, None otherwise
        """
        if not credentials:
            return None
        
        try:
            return AuthDependencies.get_current_user(credentials, db)
        except HTTPException:
            return None
    
    @staticmethod
    def get_current_admin(
        current_user: User = Depends(get_current_verified_user)
    ) -> User:
        """
        Require admin privileges
        
        Args:
            current_user: Current verified user
            
        Returns:
            Current user if admin
            
        Raises:
            HTTPException: If user is not admin
        """
        # Check if user has admin role
        # Note: You may need to add is_admin field to User model
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        return current_user
    
    @staticmethod
    def get_user_with_health_profile(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> tuple[User, Optional[HealthProfile]]:
        """
        Get current user with their health profile
        
        Args:
            current_user: Current active user
            db: Database session
            
        Returns:
            Tuple of (user, health_profile)
        """
        health_profile = db.query(HealthProfile).filter(
            HealthProfile.user_id == current_user.id
        ).first()
        
        return current_user, health_profile
    
    @staticmethod
    def require_health_profile(
        user_and_profile: tuple[User, Optional[HealthProfile]] = Depends(get_user_with_health_profile)
    ) -> tuple[User, HealthProfile]:
        """
        Require user to have a health profile
        
        Args:
            user_and_profile: Tuple from get_user_with_health_profile
            
        Returns:
            Tuple of (user, health_profile)
            
        Raises:
            HTTPException: If user doesn't have health profile
        """
        user, health_profile = user_and_profile
        
        if health_profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Health profile required. Please complete your health information."
            )
        
        return user, health_profile
    
    @staticmethod
    def verify_token_only(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
    ) -> dict:
        """
        Verify token without loading user from database
        Useful for lightweight token validation
        
        Args:
            credentials: HTTP Bearer credentials
            
        Returns:
            Token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        payload = JWTHandler.decode_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    
    @staticmethod
    def rate_limit_by_user(
        current_user: User = Depends(get_current_user),
        request: Request = None
    ) -> User:
        """
        Rate limiting by user (placeholder for future implementation)
        
        Args:
            current_user: Current authenticated user
            request: FastAPI request object
            
        Returns:
            Current user
        """
        # TODO: Implement rate limiting logic
        # For now, just return the user
        return current_user


# Convenience aliases for common dependencies
CurrentUser = Annotated[User, Depends(AuthDependencies.get_current_user)]
CurrentActiveUser = Annotated[User, Depends(AuthDependencies.get_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(AuthDependencies.get_current_verified_user)]
OptionalUser = Annotated[Optional[User], Depends(AuthDependencies.get_optional_user)]
CurrentAdmin = Annotated[User, Depends(AuthDependencies.get_current_admin)]
UserWithHealthProfile = Annotated[
    tuple[User, Optional[HealthProfile]], 
    Depends(AuthDependencies.get_user_with_health_profile)
]
UserWithRequiredHealthProfile = Annotated[
    tuple[User, HealthProfile], 
    Depends(AuthDependencies.require_health_profile)
]

# Backward compatibility functions
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Backward compatibility wrapper"""
    return AuthDependencies.get_current_user(credentials, db)


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Backward compatibility wrapper"""
    return AuthDependencies.get_current_active_user(current_user)


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Backward compatibility wrapper"""
    return AuthDependencies.get_optional_user(credentials, db)


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Backward compatibility wrapper"""
    return AuthDependencies.get_current_admin(current_user)


def verify_token_only(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    """Backward compatibility wrapper"""
    return AuthDependencies.verify_token_only(credentials)