"""
Authentication Service
======================
Business logic for user authentication (login, register, user info).
Uses centralized MySQL connection pool.
"""

from app.utils.helpers import hash_password, verify_password, create_access_token
from app.database.connection import get_pool


async def register_user(username: str, password: str):
    """
    Register a new user.

    Args:
        username: Desired username
        password: Plain text password

    Returns:
        dict: Result with success status and user data or error message
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Check if username already exists
            await cur.execute(
                "SELECT id FROM users WHERE username = %s", (username,)
            )
            existing = await cur.fetchone()

            if existing:
                return {"success": False, "message": "Username sudah terdaftar"}

            # Hash password and insert user
            pwd_hash = hash_password(password)
            await cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, pwd_hash, "user")
            )
            await conn.commit()

            user_id = cur.lastrowid

            # Create access token
            token = create_access_token(user_id, username, "user")

            return {
                "success": True,
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "username": username,
                    "role": "user"
                }
            }


async def login_user(username: str, password: str):
    """
    Authenticate a user and return a JWT token.

    Args:
        username: Username
        password: Plain text password

    Returns:
        dict: Result with token and user data, or error message
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, username, password_hash, role, created_at FROM users WHERE username = %s",
                (username,)
            )
            user = await cur.fetchone()

            if not user:
                return {"success": False, "message": "Username tidak ditemukan"}

            # Verify password
            if not verify_password(password, user["password_hash"]):
                return {"success": False, "message": "Password salah"}

            # Create access token
            token = create_access_token(user["id"], user["username"], user["role"])

            return {
                "success": True,
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "role": user["role"],
                    "created_at": str(user["created_at"]) if user["created_at"] else None
                }
            }


async def get_user_by_id(user_id: int):
    """
    Get user info by ID.

    Args:
        user_id: User's database ID

    Returns:
        dict or None: User data if found
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, username, role, created_at FROM users WHERE id = %s",
                (user_id,)
            )
            user = await cur.fetchone()

            if user:
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "role": user["role"],
                    "created_at": str(user["created_at"]) if user["created_at"] else None
                }
            return None
