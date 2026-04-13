"""
Admin Routes
============
API endpoints for admin-only operations:
dataset management, model training, and user management.
"""

from fastapi import APIRouter, Request, UploadFile, File
from app.controllers.admin_controller import (
    handle_get_dashboard,
    handle_upload_dataset,
    handle_trigger_training,
    handle_get_training_logs,
    handle_get_users,
    handle_delete_user,
    handle_get_dataset
)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard")
async def get_dashboard(request: Request):
    """Get admin dashboard statistics."""
    return await handle_get_dashboard(request)


@router.post("/upload-dataset")
async def upload_dataset(request: Request, file: UploadFile = File(...)):
    """
    Upload a CSV dataset file.
    
    The CSV must contain columns: peminatan, brand, posisi, label_sepatu.
    Records are validated and imported into the database.
    """
    return await handle_upload_dataset(request, file)


@router.post("/train")
async def trigger_training(request: Request):
    """
    Trigger model training using the current dataset.
    Returns training metrics (accuracy, precision, recall, F1-score).
    """
    return await handle_trigger_training(request)


@router.get("/training-logs")
async def get_training_logs(request: Request):
    """Get all model training history logs."""
    return await handle_get_training_logs(request)


@router.get("/users")
async def get_users(request: Request):
    """Get list of all registered users."""
    return await handle_get_users(request)


@router.delete("/users/{user_id}")
async def delete_user(request: Request, user_id: int):
    """Delete a user account (cannot delete admin)."""
    return await handle_delete_user(request, user_id)


@router.get("/dataset")
async def get_dataset(request: Request):
    """Get all dataset records."""
    return await handle_get_dataset(request)
