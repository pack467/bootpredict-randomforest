"""
Shoe Admin Routes
=================
Admin routes for managing the shoe catalog.
"""

from fastapi import APIRouter, Request, UploadFile, File, Form
from typing import Optional
from app.controllers.shoe_admin_controller import (
    handle_admin_shoes_list,
    handle_admin_shoe_add_form,
    handle_admin_shoe_create,
    handle_admin_shoe_edit_form,
    handle_admin_shoe_update,
    handle_admin_shoe_delete
)

router = APIRouter(prefix="/admin/shoes", tags=["Admin Shoes"])

@router.get("")
@router.get("/")
async def list_shoes(request: Request):
    """List all shoes in admin panel."""
    return await handle_admin_shoes_list(request)

@router.get("/add")
async def add_shoe_form(request: Request):
    """Show form to add a new shoe."""
    return await handle_admin_shoe_add_form(request)

@router.post("/add")
async def create_shoe(
    request: Request,
    name: str = Form(...),
    brand: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    stock: int = Form(0),
    sizes_available: str = Form("[]"),
    image: Optional[UploadFile] = File(None)
):
    """Process add shoe form."""
    return await handle_admin_shoe_create(
        request, name, brand, category, price, description, stock, sizes_available, image
    )

@router.get("/{shoe_id}/edit")
async def edit_shoe_form(request: Request, shoe_id: int):
    """Show form to edit a shoe."""
    return await handle_admin_shoe_edit_form(request, shoe_id)

@router.post("/{shoe_id}/edit")
async def update_shoe(
    request: Request,
    shoe_id: int,
    name: str = Form(...),
    brand: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    stock: int = Form(0),
    sizes_available: str = Form("[]"),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None)
):
    """Process edit shoe form."""
    return await handle_admin_shoe_update(
        request, shoe_id, name, brand, category, price, description, stock, sizes_available, is_active, image
    )

@router.post("/{shoe_id}/delete")
async def delete_shoe(request: Request, shoe_id: int):
    """Soft delete a shoe."""
    return await handle_admin_shoe_delete(request, shoe_id)
