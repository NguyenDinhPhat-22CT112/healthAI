"""
Password Hashing - Secure password hashing and verification
"""
import secrets
import string
from passlib.context import CryptContext
from passlib.hash import bcrypt


class PasswordHasher:
    """
    Secure password hashing using bcrypt
    """
    
    def __init__(self):
        """Initialize password context with bcrypt"""
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto",
            bcrypt__rounds=12  # Higher rounds for better security
        )
    
    def hash_password(self, password: str) -> str:
        """
        Hash a plain text password
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored hash to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False
    
    def needs_update(self, hashed_password: str) -> bool:
        """
        Check if password hash needs to be updated
        
        Args:
            hashed_password: Existing password hash
            
        Returns:
            True if hash should be updated, False otherwise
        """
        return self.pwd_context.needs_update(hashed_password)
    
    def generate_random_password(self, length: int = 12) -> str:
        """
        Generate a secure random password
        
        Args:
            length: Password length (default 12)
            
        Returns:
            Random password string
        """
        if length < 8:
            length = 8
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Fill the rest randomly
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def validate_password_strength(self, password: str) -> dict:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "is_valid": True,
            "score": 0,
            "issues": [],
            "suggestions": []
        }
        
        # Length check
        if len(password) < 8:
            result["is_valid"] = False
            result["issues"].append("Mật khẩu phải có ít nhất 8 ký tự")
        elif len(password) >= 12:
            result["score"] += 2
        else:
            result["score"] += 1
        
        # Character variety checks
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not has_lower:
            result["issues"].append("Cần có ít nhất 1 chữ thường")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        if not has_upper:
            result["issues"].append("Cần có ít nhất 1 chữ hoa")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        if not has_digit:
            result["issues"].append("Cần có ít nhất 1 số")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        if not has_special:
            result["suggestions"].append("Nên có ký tự đặc biệt để tăng bảo mật")
        else:
            result["score"] += 2
        
        # Common password check
        common_passwords = [
            "password", "123456", "123456789", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey"
        ]
        
        if password.lower() in common_passwords:
            result["is_valid"] = False
            result["issues"].append("Mật khẩu quá phổ biến, dễ bị đoán")
        
        # Sequential characters check
        if any(password[i:i+3] in "abcdefghijklmnopqrstuvwxyz123456789" 
               for i in range(len(password) - 2)):
            result["suggestions"].append("Tránh dùng ký tự liên tiếp (abc, 123)")
        
        # Repeated characters check
        if any(password[i] == password[i+1] == password[i+2] 
               for i in range(len(password) - 2)):
            result["suggestions"].append("Tránh lặp ký tự liên tiếp (aaa, 111)")
        
        # Score interpretation
        if result["score"] >= 7:
            result["strength"] = "Rất mạnh"
        elif result["score"] >= 5:
            result["strength"] = "Mạnh"
        elif result["score"] >= 3:
            result["strength"] = "Trung bình"
        else:
            result["strength"] = "Yếu"
        
        return result


# Global instance
password_hasher = PasswordHasher()

# Convenience functions for backward compatibility
def get_password_hash(password: str) -> str:
    """Hash a password"""
    return password_hasher.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return password_hasher.verify_password(plain_password, hashed_password)


def generate_random_password(length: int = 12) -> str:
    """Generate a random password"""
    return password_hasher.generate_random_password(length)


def validate_password_strength(password: str) -> dict:
    """Validate password strength"""
    return password_hasher.validate_password_strength(password)