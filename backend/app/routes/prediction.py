"""
Prediction Routes
=================
API endpoints for making boot classification predictions.
"""

from fastapi import APIRouter, Request
from app.models.prediction import PredictionRequest
from app.controllers.prediction_controller import handle_predict

router = APIRouter(prefix="/api", tags=["Prediction"])


@router.post("/predict")
async def predict(request: Request, data: PredictionRequest):
    """
    Submit a prediction request.
    
    Requires authentication. Classifies the user's preferences and returns:
    - Predicted boot category
    - Class probabilities
    - Feature importance values
    - AI explanation (in Indonesian)
    - Recommended products
    """
    return await handle_predict(request, data.peminatan, data.brand, data.posisi)
