"""
Database Connection Module
==========================
Manages MySQL database connections using aiomysql connection pool
for async operations compatible with FastAPI's async request handling.
"""

import aiomysql
from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# Global connection pool (initialized on app startup)
_pool: aiomysql.Pool = None


async def init_pool():
    """
    Initialize the global MySQL connection pool.
    Called once during application startup.
    """
    global _pool
    _pool = await aiomysql.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        autocommit=True,
        minsize=2,
        maxsize=10,
        charset="utf8mb4",
        cursorclass=aiomysql.DictCursor,
    )
    print(f"[DB] Connection pool created: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


async def close_pool():
    """
    Close the global MySQL connection pool.
    Called during application shutdown.
    """
    global _pool
    if _pool:
        _pool.close()
        await _pool.wait_closed()
        _pool = None
        print("[DB] Connection pool closed.")


async def get_db():
    """
    Async context-manager dependency for FastAPI route handlers.
    Acquires a connection from the pool and returns it.

    Yields:
        aiomysql.Connection: Active database connection with DictCursor
    """
    global _pool
    async with _pool.acquire() as conn:
        try:
            yield conn
        finally:
            pass  # connection returned to pool automatically


async def get_db_connection():
    """
    Get a standalone database connection from the pool (not as dependency).
    Caller is responsible for releasing the connection.

    Returns:
        aiomysql.Connection: Active database connection
    """
    global _pool
    conn = await _pool.acquire()
    return conn


def get_pool():
    """Return the global pool reference."""
    return _pool
