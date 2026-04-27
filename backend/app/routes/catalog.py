"""
Catalog Routes
==============
Public routes for the shoe catalog.
"""

from fastapi import APIRouter, Request, Query
from typing import Optional
from app.controllers.catalog_controller import handle_catalog_page, handle_shoe_detail

router = APIRouter(prefix="/catalog", tags=["Catalog"])

@router.get("")
@router.get("/")
async def catalog_index(
    request: Request,
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[str] = Query(None),
    max_price: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    page: int = Query(1, ge=1)
):
    """Render the public catalog listing page."""
    # Parse price strings to float, ignoring empty values
    parsed_min_price = None
    parsed_max_price = None
    try:
        if min_price and min_price.strip():
            parsed_min_price = float(min_price)
    except (ValueError, TypeError):
        pass
    try:
        if max_price and max_price.strip():
            parsed_max_price = float(max_price)
    except (ValueError, TypeError):
        pass
    
    return await handle_catalog_page(request, category, brand, search, parsed_min_price, parsed_max_price, sort, page)

@router.get("/{shoe_id}")
async def shoe_detail(request: Request, shoe_id: int):
    """Render the public shoe detail page with recommendations."""
    return await handle_shoe_detail(request, shoe_id)
