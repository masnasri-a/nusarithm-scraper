"""
Authentication and user management endpoints
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uuid

try:
    from ..models.auth import (
        User, UserCreate, UserLogin, Token, TokenData, APITokenCreate, APIToken,
        verify_password, get_password_hash, create_access_token, verify_token,
        generate_api_token, ACCESS_TOKEN_EXPIRE_MINUTES
    )
    from ..db import template_store
except ImportError:
    from app.models.auth import (
        User, UserCreate, UserLogin, Token, TokenData, APITokenCreate, APIToken,
        verify_password, get_password_hash, create_access_token, verify_token,
        generate_api_token, ACCESS_TOKEN_EXPIRE_MINUTES
    )
    from app.db import template_store

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Dependency to get current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        if token_data is None or token_data.username is None:
            raise credentials_exception
        
        # Get user from database
        user_data = await template_store.get_user_by_username(token_data.username)
        if user_data is None:
            raise credentials_exception
        
        return User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            role=user_data["role"],
            is_active=user_data["is_active"],
            created_at=user_data["created_at"],
            train_count=user_data["train_count"],
            scrape_count=user_data["scrape_count"],
            max_trains=user_data["max_trains"],
            max_scrapes=user_data["max_scrapes"]
        )
    except Exception as e:
        raise credentials_exception

# Alternative dependency for API token authentication
async def get_current_user_from_api_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from API token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate API token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # First try JWT token
        token_data = verify_token(token)
        if token_data and token_data.username:
            user_data = await template_store.get_user_by_username(token_data.username)
            if user_data:
                return User(
                    id=user_data["id"],
                    username=user_data["username"],
                    email=user_data["email"],
                    role=user_data["role"],
                    is_active=user_data["is_active"],
                    created_at=user_data["created_at"],
                    train_count=user_data["train_count"],
                    scrape_count=user_data["scrape_count"],
                    max_trains=user_data["max_trains"],
                    max_scrapes=user_data["max_scrapes"]
                )
        
        # Try API token
        user_data = await template_store.get_user_by_api_token(token)
        if user_data is None:
            raise credentials_exception
        
        return User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            role=user_data["role"],
            is_active=user_data["is_active"],
            created_at=user_data["created_at"],
            train_count=user_data["train_count"],
            scrape_count=user_data["scrape_count"],
            max_trains=user_data["max_trains"],
            max_scrapes=user_data["max_scrapes"]
        )
        
    except Exception as e:
        raise credentials_exception

# Check if user has permission for action
def check_user_limits(user: User, action: str) -> bool:
    """Check if user has permission to perform action"""
    if user.role == "admin":
        return True
        
    if action == "train":
        return user.max_trains == -1 or user.train_count < user.max_trains
    elif action == "scrape":
        return user.max_scrapes == -1 or user.scrape_count < user.max_scrapes
    
    return False

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    """Register a new user"""
    
    # Check if username already exists
    existing_user = await template_store.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    new_user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": hashed_password,
        "role": "user",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "train_count": 0,
        "scrape_count": 0,
        "max_trains": 1,  # Free trial
        "max_scrapes": 10  # Free trial
    }
    
    await template_store.create_user(new_user)
    
    return {
        "message": "User registered successfully",
        "username": user_data.username,
        "email": user_data.email
    }

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user and return JWT token"""
    
    # Get user from database
    user_data = await template_store.get_user_by_username(user_credentials.username)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user_data["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Check if user is active
    if not user_data["is_active"]:
        raise HTTPException(
            status_code=401,
            detail="Account is disabled"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["username"]}, 
        expires_delta=access_token_expires
    )
    
    user = User(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        role=user_data["role"],
        is_active=user_data["is_active"],
        created_at=user_data["created_at"],
        train_count=user_data["train_count"],
        scrape_count=user_data["scrape_count"],
        max_trains=user_data["max_trains"],
        max_scrapes=user_data["max_scrapes"]
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/tokens", response_model=APIToken)
async def create_api_token(
    token_request: APITokenCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new API token"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create API tokens"
        )
    
    # Generate token
    token_id = str(uuid.uuid4())
    token = generate_api_token()
    
    expires_at = None
    if token_request.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=token_request.expires_in_days)
    
    token_data = {
        "id": token_id,
        "name": token_request.name,
        "token": token,
        "user_id": current_user.id,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "is_active": True
    }
    
    await template_store.create_api_token(token_data)
    
    return APIToken(
        id=token_id,
        name=token_request.name,
        token=token,
        user_id=current_user.id,
        created_at=token_data["created_at"],
        expires_at=expires_at,
        is_active=True
    )

@router.get("/validate")
async def validate_token(current_user: User = Depends(get_current_user_from_api_token)):
    """Validate token and return user info"""
    return {
        "valid": True,
        "user": current_user,
        "message": "Token is valid"
    }