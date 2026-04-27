"""
Application Configuration
=========================
Central configuration file for the Football Boots Classification System.
Uses environment variables with fallback defaults for sensitive values.
"""

import os

# Base directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
APP_DIR = os.path.join(BASE_DIR, "app")

# ==========================================
# MySQL Database Configuration
# ==========================================
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "galih0249")
DB_NAME = os.environ.get("DB_NAME", "football_boots_db")

# ML Model paths
ML_DIR = os.path.join(APP_DIR, "ml")
MODEL_PATH = os.path.join(ML_DIR, "model.pkl")
ENCODERS_PATH = os.path.join(ML_DIR, "encoders.pkl")

# Dataset paths
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")
DATASET_CSV_PATH = os.path.join(DATASET_DIR, "sepatu_dataset.csv")
PRODUCT_CATALOG_PATH = os.path.join(DATASET_DIR, "produk_sepatu.json")

# Frontend path
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# Shoe catalog settings
UPLOAD_DIR = os.path.join(FRONTEND_DIR, "static", "uploads", "shoes")
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# Template directory (for Jinja2 server-rendered pages)
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")

# Auth settings
SECRET_KEY = os.environ.get("SECRET_KEY", "football-boots-classifier-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Default admin credentials
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

# Valid categorical values
VALID_PEMINATAN = ["speed", "control", "power"]
VALID_BRAND = ["nike", "adidas", "puma", "mizuno", "umbro"]
VALID_POSISI = ["striker", "midfielder", "defender", "goalkeeper"]
VALID_LABELS = ["speed_boot", "control_boot", "power_boot"]
