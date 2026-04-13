"""
History Controller
==================
Handles request processing for prediction history endpoints.
"""

from fastapi import Request, HTTPException
from app.services.history_service import get_user_history, delete_history_item, get_user_stats
from app.utils.helpers import get_current_user_from_request


async def handle_get_history(request: Request):
    """
    Get prediction history for the current authenticated user.
    
    Args:
        request: FastAPI request object
    
    Returns:
        list: User's prediction history
    """
    user_payload = get_current_user_from_request(request)
    user_id = int(user_payload["sub"])
    
    return await get_user_history(user_id)


async def handle_delete_history(request: Request, prediction_id: int):
    """
    Delete a prediction history entry.
    
    Args:
        request: FastAPI request object
        prediction_id: ID of prediction to delete
    
    Returns:
        dict: Deletion result
    
    Raises:
        HTTPException: If deletion fails
    """
    user_payload = get_current_user_from_request(request)
    user_id = int(user_payload["sub"])
    
    result = await delete_history_item(prediction_id, user_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


async def handle_get_stats(request: Request):
    """
    Get prediction statistics for the current user.
    
    Args:
        request: FastAPI request object
    
    Returns:
        dict: User statistics
    """
    user_payload = get_current_user_from_request(request)
    user_id = int(user_payload["sub"])
    
    return await get_user_stats(user_id)
