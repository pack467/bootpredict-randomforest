"""
Dataset Model
=============
Pydantic models for dataset-related schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional


class DatasetRecord(BaseModel):
    """Schema for a single dataset record."""
    peminatan: str
    brand: str
    posisi: str
    label_sepatu: str
    source: str = "manual"


class TrainingLogResponse(BaseModel):
    """Schema for training log entry."""
    id: int
    accuracy: Optional[float] = None
    precision_score: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    dataset_size: Optional[int] = None
    n_estimators: Optional[int] = None
    trained_at: Optional[str] = None
