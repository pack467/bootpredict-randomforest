"""
Database Initialization Module
==============================
Creates the MySQL database (if needed), all required tables,
and seeds default data (admin user + shoe catalog).
Called on application startup.
"""

import aiomysql
import bcrypt
import json
import os
import re
from app.config import (
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME,
    DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD,
    PRODUCT_CATALOG_PATH,
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

            # Shoes table - for catalog
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS shoes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    brand VARCHAR(100) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    price DECIMAL(12, 2) NOT NULL DEFAULT 0,
                    description TEXT,
                    image_filename VARCHAR(255) DEFAULT NULL,
                    stock INT DEFAULT 0,
                    sizes_available JSON,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_brand (brand),
                    INDEX idx_category (category),
                    INDEX idx_is_active (is_active),
                    INDEX idx_price (price)
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

        # ==========================================
        # SEED SHOE CATALOG FROM JSON
        # ==========================================
        await _seed_shoes_from_catalog(conn)

    finally:
        conn.close()

    print("[DB] Database initialization complete.")


def _parse_price(price_str: str) -> float:
    """
    Parse Indonesian Rupiah price string to float.
    Examples: 'Rp 3.500.000' -> 3500000.0, 'Rp 800.000' -> 800000.0
    """
    if isinstance(price_str, (int, float)):
        return float(price_str)
    # Remove 'Rp', spaces, and dots used as thousand separators
    cleaned = re.sub(r'[Rp\s.]', '', str(price_str))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


async def _seed_shoes_from_catalog(conn):
    """
    Seed the shoes table from produk_sepatu.json if the table is empty.
    This ensures the catalog has data on first startup.
    """
    async with conn.cursor() as cur:
        await cur.execute("SELECT COUNT(*) as cnt FROM shoes")
        result = await cur.fetchone()
        count = result["cnt"] if result else 0

        if count > 0:
            print(f"[DB] Shoes table already has {count} records. Skipping seed.")
            return

    # Load the product catalog JSON
    if not os.path.exists(PRODUCT_CATALOG_PATH):
        print(f"[DB] Product catalog not found at {PRODUCT_CATALOG_PATH}. Skipping shoe seed.")
        return

    with open(PRODUCT_CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    shoes_to_insert = []
    for category, brands in catalog.items():
        for brand_key, products in brands.items():
            for product in products:
                price = _parse_price(product.get("price", 0))
                description = product.get("description", "")
                features = product.get("features", [])
                if features:
                    description += "\n\nFitur: " + ", ".join(features)

                # Map the image path to an image_filename for the catalog
                # The JSON uses /static/images/... paths, store just the filename
                image_path = product.get("image", "")
                image_filename = None
                if image_path:
                    # Store the full static path so the template can use it
                    # We'll handle this in the template with a fallback
                    image_filename = image_path  # Keep the static path

                shoes_to_insert.append((
                    product.get("name", "Unknown"),
                    product.get("brand", brand_key.title()),
                    category,
                    price,
                    description,
                    image_filename,
                    10,  # default stock
                    json.dumps(["39", "40", "41", "42", "43", "44", "45"]),  # default sizes
                ))

    if not shoes_to_insert:
        print("[DB] No shoes found in catalog JSON. Skipping seed.")
        return

    async with conn.cursor() as cur:
        query = """
            INSERT INTO shoes 
            (name, brand, category, price, description, image_filename, stock, sizes_available)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        await cur.executemany(query, shoes_to_insert)
    await conn.commit()
    print(f"[DB] Seeded {len(shoes_to_insert)} shoes from product catalog.")
