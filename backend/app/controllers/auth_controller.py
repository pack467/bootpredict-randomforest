"""
Authentication Controller
=========================
Handles request processing for auth-related endpoints.
Bridges between routes and auth service.
"""

from fastapi import Request, HTTPException
from app.services.auth_service import register_user, login_user, get_user_by_id
from app.utils.helpers import get_current_user_from_request


async def handle_register(username: str, password: str):
    """
    Process user registration request.
    
    Args:
        username: Desired username
        password: Password
    
    Returns:
        dict: Registration result
    
    Raises:
        HTTPException: If registration fails
    """
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username minimal 3 karakter")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password minimal 4 karakter")
    
    result = await register_user(username, password)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


async def handle_login(username: str, password: str):
    """
    Process user login request.
    
    Args:
        username: Username
        password: Password
    
    Returns:
        dict: Login result with token
    
    Raises:
        HTTPException: If login fails
    """
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username dan password harus diisi")
    
    result = await login_user(username, password)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    
    return result


async def handle_get_me(request: Request):
    """
    Get current authenticated user info.
    
    Args:
        request: FastAPI request object
    
    Returns:
        dict: Current user data
    """
    user_payload = get_current_user_from_request(request)
    user_id = int(user_payload["sub"])
    
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    return user
