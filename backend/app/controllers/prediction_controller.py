"""
Prediction Controller
=====================
Handles request processing for prediction endpoints.
"""

from fastapi import Request, HTTPException
from app.services.prediction_service import make_prediction
from app.utils.helpers import get_current_user_from_request


async def handle_predict(request: Request, peminatan: str, brand: str, posisi: str):
    """
    Process a prediction request from an authenticated user.
    
    Args:
        request: FastAPI request object
        peminatan: Play style preference
        brand: Preferred brand
        posisi: Player position
    
    Returns:
        dict: Prediction results
    
    Raises:
        HTTPException: If prediction fails
    """
    # Get current user from token
    user_payload = get_current_user_from_request(request)
    user_id = int(user_payload["sub"])
    
    # Make prediction
    result = await make_prediction(user_id, peminatan, brand, posisi)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result["data"]
