"""
Shoe Admin Controller
=====================
Handles request processing for admin shoe management pages.
"""

from fastapi import Request, UploadFile, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.config import TEMPLATE_DIR, UPLOAD_DIR, ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE
from app.services.shoe_service import get_all_shoes, get_shoe_by_id, create_shoe, update_shoe, soft_delete_shoe
from app.utils.helpers import decode_access_token
import os
import uuid
import json

templates = Jinja2Templates(directory=TEMPLATE_DIR)

def get_admin_user_from_cookie(request: Request):
    """Extract admin user from JWT token stored in cookie."""
    token = request.cookies.get("access_token")
    if not token:
        # Fallback to Authorization header for API calls
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        return None
        
    try:
        user_payload = decode_access_token(token)
        if user_payload.get("role") != "admin":
            return None
        return user_payload
    except:
        return None

async def handle_admin_shoes_list(request: Request):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    shoes_data = await get_all_shoes(include_inactive=True, page_size=100) # Get more for admin list
    
    return templates.TemplateResponse("admin/shoes/index.html", {
        "request": request,
        "shoes": shoes_data["items"]
    })

async def handle_admin_shoe_add_form(request: Request):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    return templates.TemplateResponse("admin/shoes/form.html", {
        "request": request,
        "shoe": None
    })

async def save_upload_file(file: UploadFile) -> str:
    if not file or not file.filename:
        return None
        
    # Check extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Tipe file .{ext} tidak diizinkan")
        
    # Generate unique filename
    filename = f"{uuid.uuid4().hex}_{file.filename.replace(' ', '_')}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Check size & save
    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran file terlalu besar (Maks 5MB)")
        
    with open(filepath, "wb") as f:
        f.write(contents)
        
    return filename

async def handle_admin_shoe_create(
    request: Request,
    name: str = Form(...),
    brand: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    stock: int = Form(0),
    sizes_available: str = Form("[]"),
    image: UploadFile = None
):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    try:
        sizes = json.loads(sizes_available)
    except json.JSONDecodeError:
        sizes = []

    image_filename = None
    if image and image.filename:
        image_filename = await save_upload_file(image)

    data = {
        "name": name,
        "brand": brand,
        "category": category,
        "price": price,
        "description": description,
        "stock": stock,
        "sizes_available": sizes,
        "image_filename": image_filename
    }
    
    await create_shoe(data)
    
    return RedirectResponse(url="/admin/shoes", status_code=303)

async def handle_admin_shoe_edit_form(request: Request, shoe_id: int):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    shoe = await get_shoe_by_id(shoe_id)
    if not shoe:
        raise HTTPException(status_code=404, detail="Sepatu tidak ditemukan")
        
    return templates.TemplateResponse("admin/shoes/form.html", {
        "request": request,
        "shoe": shoe
    })

async def handle_admin_shoe_update(
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
    image: UploadFile = None
):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    try:
        sizes = json.loads(sizes_available)
    except json.JSONDecodeError:
        sizes = []

    data = {
        "name": name,
        "brand": brand,
        "category": category,
        "price": price,
        "description": description,
        "stock": stock,
        "sizes_available": sizes,
        "is_active": is_active
    }
    
    if image and image.filename:
        data["image_filename"] = await save_upload_file(image)
        
    await update_shoe(shoe_id, data)
    
    return RedirectResponse(url="/admin/shoes", status_code=303)

async def handle_admin_shoe_delete(request: Request, shoe_id: int):
    user = get_admin_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
        
    await soft_delete_shoe(shoe_id)
    
    return RedirectResponse(url="/admin/shoes", status_code=303)
