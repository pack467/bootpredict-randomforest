"""
Football Boots Classification & Recommendation System
=====================================================
Main FastAPI Application Entry Point

This application provides:
- User authentication (login/register)
- Boot classification using Random Forest ML model
- Explainable AI with feature importance
- Product recommendations
- Admin panel for dataset/model management

Database: MySQL (aiomysql connection pool)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import FRONTEND_DIR, MODEL_PATH, UPLOAD_DIR
from app.database.init_db import init_database
from app.database.connection import init_pool, close_pool
from app.routes import auth, prediction, history, admin, catalog, shoe_admin


# ==========================================
# LIFESPAN (replaces deprecated on_event)
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    - Startup: Initialize database, create connection pool
    - Shutdown: Close connection pool
    """
    # === STARTUP ===
    print("\n" + "=" * 60)
    print("  Football Boots Classification System - Starting...")
    print("=" * 60)

    # 1. Initialize database tables & seed admin
    await init_database()

    # 2. Create MySQL connection pool
    await init_pool()

    # 3. Check if trained model exists
    if os.path.exists(MODEL_PATH):
        print(f"[ML] Trained model found: {MODEL_PATH}")
    else:
        print(f"[ML] No trained model found. Admin must train the model first.")

    # 4. Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    print(f"[Storage] Upload directory ensured at {UPLOAD_DIR}")

    print("\n[OK] Application ready!")
    print(f"Frontend directory: {FRONTEND_DIR}")
    print(f"Open http://localhost:8000 in your browser")
    print("=" * 60 + "\n")

    yield  # Application is running

    # === SHUTDOWN ===
    print("\n[SHUTDOWN] Closing resources...")
    await close_pool()
    print("[SHUTDOWN] Complete.")


# ==========================================
# APP INITIALIZATION
# ==========================================

app = FastAPI(
    title="Football Boots Classifier",
    description="Sistem Klasifikasi dan Rekomendasi Sepatu Bola menggunakan Random Forest",
    version="1.0.0",
    lifespan=lifespan,
)

# ==========================================
# MIDDLEWARE
# ==========================================

# CORS - allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for thesis demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ROUTES
# ==========================================

# Include API route modules
app.include_router(auth.router)
app.include_router(prediction.router)
app.include_router(history.router)
app.include_router(admin.router)

# Include Jinja2 route modules
app.include_router(catalog.router)
app.include_router(shoe_admin.router)

# ==========================================
# STATIC FILES & FRONTEND SERVING
# ==========================================

# Serve static assets (CSS, JS, images)
static_dir = os.path.join(FRONTEND_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount uploads directory specifically so we can serve images
if os.path.exists(UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ==========================================
# FRONTEND PAGE ROUTES
# ==========================================

@app.get("/")
async def serve_login():
    """Serve the login page as the default landing page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


@app.get("/login")
async def serve_login_page():
    """Serve the login page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


@app.get("/register")
async def serve_register_page():
    """Serve the registration page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "register.html"))


@app.get("/dashboard")
async def serve_dashboard():
    """Serve the user dashboard / prediction form page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))


@app.get("/result")
async def serve_result():
    """Serve the prediction result page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "result.html"))


@app.get("/history")
async def serve_history():
    """Serve the prediction history page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "history.html"))


@app.get("/admin")
async def serve_admin():
    """Serve the admin panel page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "admin.html"))


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/api/health")
async def health_check():
    """API health check endpoint."""
    return {"status": "ok", "message": "Football Boots Classifier API is running"}
