"""
Authentication Routes
=====================
API endpoints for user login, registration, and session management.
"""

from fastapi import APIRouter, Request
from app.models.user import UserLogin, UserRegister
from app.controllers.auth_controller import handle_register, handle_login, handle_get_me

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register")
async def register(data: UserRegister):
    """
    Register a new user account.
    
    - **username**: Unique username (min 3 chars)
    - **password**: Account password (min 4 chars)
    """
    return await handle_register(data.username, data.password)


@router.post("/login")
async def login(data: UserLogin):
    """
    Login with username and password.
    Returns a JWT token for authenticated requests.
    """
    return await handle_login(data.username, data.password)


@router.get("/me")
async def get_current_user(request: Request):
    """
    Get the currently authenticated user's information.
    Requires a valid Bearer token in the Authorization header.
    """
    return await handle_get_me(request)
