"""
Prediction Model
================
Pydantic models for prediction request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime


class PredictionRequest(BaseModel):
    """Schema for prediction input from user."""
    peminatan: str = Field(
        ..., 
        description="Play style preference: speed, control, or power"
    )
    brand: str = Field(
        ..., 
        description="Preferred brand: nike, adidas, puma, mizuno, or umbro"
    )
    posisi: str = Field(
        ..., 
        description="Player position: striker, midfielder, defender, or goalkeeper"
    )


class PredictionResponse(BaseModel):
    """Schema for prediction result."""
    predicted_class: str
    predicted_label: str
    probabilities: Dict[str, float]
    feature_importance: Dict[str, float]
    explanation: str
    input: Dict[str, str]
    recommended_products: Optional[List[dict]] = None


class PredictionHistoryItem(BaseModel):
    """Schema for a single prediction history entry."""
    id: int
    peminatan: str
    brand: str
    posisi: str
    predicted_class: str
    probabilities: Optional[str] = None
    feature_importance: Optional[str] = None
    explanation: Optional[str] = None
    created_at: Optional[str] = None
