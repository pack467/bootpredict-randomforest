"""
Shoe Model
==========
Pydantic models for shoe-related request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ShoeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    brand: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., ge=0)
    description: Optional[str] = None
    stock: int = Field(0, ge=0)
    sizes_available: Optional[List[str]] = None

class ShoeCreate(ShoeBase):
    pass

class ShoeUpdate(ShoeBase):
    is_active: Optional[bool] = None

class ShoeResponse(ShoeBase):
    id: int
    image_filename: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ShoeFilter(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(12, ge=1, le=100)
