"""
Catalog Controller
==================
Handles request processing for public catalog pages.
"""

from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from app.config import TEMPLATE_DIR
from app.services.shoe_service import (
    get_all_shoes, get_shoe_by_id,
    get_distinct_brands, get_distinct_categories,
    get_price_range
)
from app.services.recommendation_service import get_recommendations

templates = Jinja2Templates(directory=TEMPLATE_DIR)

async def handle_catalog_page(
    request: Request,
    category: str = None,
    brand: str = None,
    search: str = None,
    min_price: float = None,
    max_price: float = None,
    sort: str = None,
    page: int = 1
):
    filters = {}
    if category: filters['category'] = category
    if brand: filters['brand'] = brand
    if search: filters['search'] = search
    if min_price is not None: filters['min_price'] = min_price
    if max_price is not None: filters['max_price'] = max_price
    
    shoes_data = await get_all_shoes(filters=filters, page=page, sort_by=sort)
    brands = await get_distinct_brands()
    categories = await get_distinct_categories()
    price_range = await get_price_range()
    
    return templates.TemplateResponse("catalog/index.html", {
        "request": request,
        "shoes": shoes_data["items"],
        "pagination": {
            "total": shoes_data["total"],
            "page": shoes_data["page"],
            "pages": shoes_data["pages"]
        },
        "filters": {
            "category": category,
            "brand": brand,
            "search": search,
            "min_price": min_price,
            "max_price": max_price,
            "sort": sort
        },
        "available_brands": brands,
        "available_categories": categories,
        "price_range": price_range
    })

async def handle_shoe_detail(request: Request, shoe_id: int):
    shoe = await get_shoe_by_id(shoe_id)
    if not shoe or not shoe.get("is_active"):
        raise HTTPException(status_code=404, detail="Sepatu tidak ditemukan")
        
    recommendations = await get_recommendations(shoe_id, limit=4)
    
    return templates.TemplateResponse("catalog/detail.html", {
        "request": request,
        "shoe": shoe,
        "recommendations": recommendations
    })
