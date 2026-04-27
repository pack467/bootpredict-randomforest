"""
Admin Controller
================
Handles request processing for admin-only endpoints.
"""

from fastapi import Request, HTTPException, UploadFile
from app.services.admin_service import (
    get_dashboard_stats,
    upload_dataset_csv,
    trigger_training,
    get_training_logs,
    get_all_users,
    delete_user,
    get_dataset_records,
    clear_dataset,
    delete_trained_model
)
from app.utils.helpers import get_current_user_from_request, require_admin


async def handle_get_dashboard(request: Request):
    """Get admin dashboard statistics."""
    user_payload = get_current_user_from_request(request)
    require_admin(user_payload)
    
    return await get_dashboard_stats()


async def handle_upload_dataset(request: Request, file: UploadFile):
    """
    Handle CSV dataset upload.
    
    Args:
        request: FastAPI request object
        file: Uploaded CSV file
    
    Returns:
        dict: Import result
    """
    user_payload = get_current_user_from_request(request)
    require_admin(user_payload)
    
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File harus berformat CSV")
    
    # Read file content
    content = await file.read()
    try:
        file_content = content.decode("utf-8")
    except UnicodeDecodeError:
        file_content = content.decode("latin-1")
    
    result = await upload_dataset_csv(file_content)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


async def handle_trigger_training(request: Request):
    """Trigger model training (admin only)."""
    user_payload = get_current_user_from_request(request)
    require_admin(user_payload)
    
    result = await trigger_training()
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result


async def handle_get_training_logs(request: Request):
    """Get all training logs (admin only)."""
    user_payload = get_current_user_from_request(request)
    require_admin(user_payload)
    
    return await get_training_logs()


async def handle_get_users(request: Request):
    """Get all users (admin only)."""
    user_payload = get_current_user_from_request(request)
    require_admin(user_payload)
    
    return await get_all_users()


async def handle_delete_user(request: Request, user_id: int):
    """Delete a user (admin only)."""
    user_payload = get_current_user_from_request(request)
    require_admin(user_payload)
    
    result = await delete_user(user_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


async def handle_get_dataset(request: Request):
    """Get dataset records (admin only)."""
    user_payload = get_current_user_from_request(request)
    require_admin(user_payload)
    
    return await get_dataset_records()


async def handle_clear_dataset(request: Request):
    """Clear all dataset records (admin only)."""
    user_payload = get_current_user_from_request(request)
    require_admin(user_payload)
    
    result = await clear_dataset()
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result


async def handle_delete_model(request: Request):
    """Delete trained model and training logs (admin only)."""
    user_payload = get_current_user_from_request(request)
    require_admin(user_payload)
    
    result = await delete_trained_model()
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result
