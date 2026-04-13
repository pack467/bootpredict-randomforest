"""
Utility Helpers
===============
Shared utility functions for authentication, validation, etc.
"""

import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


def create_access_token(user_id: int, username: str, role: str) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User's database ID
        username: User's username
        role: User's role (user/admin)

    Returns:
        str: Encoded JWT token
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token telah kedaluwarsa")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token tidak valid")


def get_current_user_from_request(request: Request) -> dict:
    """
    Extract and validate the current user from the request's Authorization header.

    Args:
        request: FastAPI Request object

    Returns:
        dict: User info from token payload

    Raises:
        HTTPException: If no valid token is present
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token autentikasi tidak ditemukan. Silakan login terlebih dahulu."
        )

    token = auth_header.split(" ")[1]
    return decode_access_token(token)


def require_admin(user_payload: dict):
    """
    Check if the user has admin role.

    Args:
        user_payload: Decoded token payload

    Raises:
        HTTPException: If user is not an admin
    """
    if user_payload.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak. Hanya admin yang dapat mengakses fitur ini."
        )
