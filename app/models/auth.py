"""
User authentication and management models
"""

from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List
import os
import hashlib
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import uuid

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Password hashing
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    BCRYPT_AVAILABLE = True
except Exception as e:
    print(f"Warning: bcrypt not available, using SHA256 fallback: {e}")
    pwd_context = None
    BCRYPT_AVAILABLE = False

# User models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: str
    role: str = "user"  # user, admin
    created_at: datetime
    train_count: int = 0
    scrape_count: int = 0
    max_trains: int = 1  # Free trial: 1 train
    max_scrapes: int = 10  # Free trial: 10 scrapes
    api_tokens: List[str] = []

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class TokenData(BaseModel):
    username: Optional[str] = None

class APITokenCreate(BaseModel):
    name: str
    expires_in_days: Optional[int] = 365

class APIToken(BaseModel):
    id: str
    name: str
    token: str
    user_id: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    is_active: bool = True

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    if BCRYPT_AVAILABLE:
        return pwd_context.verify(plain_password, hashed_password)
    else:
        # Fallback to SHA256 for testing
        salt = "fallback_salt_for_testing"
        test_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return test_hash == hashed_password

def get_password_hash(password: str) -> str:
    """Hash a password"""
    if BCRYPT_AVAILABLE:
        return pwd_context.hash(password)
    else:
        # Fallback to SHA256 for testing
        salt = "fallback_salt_for_testing"
        return hashlib.sha256((password + salt).encode()).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None

def generate_api_token() -> str:
    """Generate a secure API token"""
    return secrets.token_urlsafe(32)