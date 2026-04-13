"""
Database Initialization Module
==============================
Creates the MySQL database (if needed), all required tables,
and seeds default data (admin user).
Called on application startup.
"""

import aiomysql
import bcrypt
from app.config import (
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME,
    DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD,
)


async def _ensure_database_exists():
    """
    Connect to MySQL server (without specifying a database) and
    create the application database if it does not already exist.
    """
    conn = await aiomysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8mb4",
    )
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        await conn.commit()
        print(f"[DB] Database '{DB_NAME}' ensured.")
    finally:
        conn.close()


async def init_database():
    """
    Initialize the database: create tables if they don't exist
    and seed the default admin user.

    This function is called BEFORE the connection pool is created,
    so it uses a standalone connection.
    """
    # Step 0: Ensure the database itself exists
    await _ensure_database_exists()

    # Step 1: Connect to the target database
    conn = await aiomysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        charset="utf8mb4",
        cursorclass=aiomysql.DictCursor,
    )

    try:
        async with conn.cursor() as cur:
            # ==========================================
            # CREATE TABLES
            # ==========================================

            # Users table - stores registered users and admins
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('user', 'admin') DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Predictions table - stores classification history
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    peminatan VARCHAR(20) NOT NULL,
                    brand VARCHAR(20) NOT NULL,
                    posisi VARCHAR(20) NOT NULL,
                    predicted_class VARCHAR(30) NOT NULL,
                    probabilities TEXT,
                    feature_importance TEXT,
                    explanation TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Training logs table - records model training sessions
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS training_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    accuracy DOUBLE,
                    precision_score DOUBLE,
                    recall_score DOUBLE,
                    f1_score DOUBLE,
                    cv_mean_accuracy DOUBLE,
                    cv_std_accuracy DOUBLE,
                    dataset_size INT,
                    n_estimators INT DEFAULT 100,
                    classification_report TEXT,
                    confusion_matrix TEXT,
                    feature_importance TEXT,
                    trained_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Dataset records table - for admin dataset management
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS dataset_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    peminatan VARCHAR(20) NOT NULL,
                    brand VARCHAR(20) NOT NULL,
                    posisi VARCHAR(20) NOT NULL,
                    label_sepatu VARCHAR(30) NOT NULL,
                    source ENUM('manual', 'csv_upload', 'scraped') DEFAULT 'manual',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

        await conn.commit()
        print("[DB] All tables created successfully.")

        # ==========================================
        # SEED DEFAULT ADMIN
        # ==========================================
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id FROM users WHERE username = %s",
                (DEFAULT_ADMIN_USERNAME,)
            )
            existing_admin = await cur.fetchone()

            if not existing_admin:
                # Hash the default admin password
                password_hash = bcrypt.hashpw(
                    DEFAULT_ADMIN_PASSWORD.encode("utf-8"),
                    bcrypt.gensalt()
                ).decode("utf-8")

                await cur.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    (DEFAULT_ADMIN_USERNAME, password_hash, "admin")
                )
                await conn.commit()
                print(f"[DB] Default admin created: {DEFAULT_ADMIN_USERNAME}/{DEFAULT_ADMIN_PASSWORD}")  # noqa
            else:
                print("[DB] Admin user already exists.")

    finally:
        conn.close()

    print("[DB] Database initialization complete.")
