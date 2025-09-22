"""
User management endpoints for admin
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from ..models.auth import User
from ..routers.auth import get_current_user, get_current_user_from_api_token
from ..db import template_store

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
async def get_my_profile(current_user: User = Depends(get_current_user_from_api_token)):
    """Get current user profile"""
    return current_user

@router.get("/", response_model=List[User])
async def get_all_users(current_user: User = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view all users"
        )
    
    # This would need to be implemented in the database
    # For now, return empty list
    return []

@router.get("/stats")
async def get_user_stats(current_user: User = Depends(get_current_user_from_api_token)):
    """Get current user usage statistics"""
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "train_count": current_user.train_count,
        "scrape_count": current_user.scrape_count,
        "max_trains": current_user.max_trains,
        "max_scrapes": current_user.max_scrapes,
        "trains_remaining": max(0, current_user.max_trains - current_user.train_count) if current_user.max_trains != -1 else -1,
        "scrapes_remaining": max(0, current_user.max_scrapes - current_user.scrape_count) if current_user.max_scrapes != -1 else -1,
        "account_type": "admin" if current_user.role == "admin" else "free_trial" if current_user.max_trains == 1 else "premium"
    }