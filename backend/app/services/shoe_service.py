"""
Shoe Service
============
Business logic for shoe catalog operations (CRUD).
"""

import json
from app.database.connection import get_pool

async def get_all_shoes(filters=None, page=1, page_size=12, include_inactive=False, sort_by=None):
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            query = "SELECT * FROM shoes WHERE 1=1"
            count_query = "SELECT COUNT(*) as total FROM shoes WHERE 1=1"
            params = []
            
            if not include_inactive:
                query += " AND is_active = TRUE"
                count_query += " AND is_active = TRUE"
            
            if filters:
                if filters.get("category"):
                    query += " AND category = %s"
                    count_query += " AND category = %s"
                    params.append(filters["category"])
                if filters.get("brand"):
                    query += " AND brand = %s"
                    count_query += " AND brand = %s"
                    params.append(filters["brand"])
                if filters.get("min_price"):
                    query += " AND price >= %s"
                    count_query += " AND price >= %s"
                    params.append(filters["min_price"])
                if filters.get("max_price"):
                    query += " AND price <= %s"
                    count_query += " AND price <= %s"
                    params.append(filters["max_price"])
                if filters.get("search"):
                    query += " AND (name LIKE %s OR brand LIKE %s OR category LIKE %s OR description LIKE %s)"
                    count_query += " AND (name LIKE %s OR brand LIKE %s OR category LIKE %s OR description LIKE %s)"
                    search_term = f"%{filters['search']}%"
                    params.extend([search_term, search_term, search_term, search_term])
            
            # Count total
            await cur.execute(count_query, params)
            total_res = await cur.fetchone()
            total = total_res["total"] if total_res else 0
            
            # Sorting
            sort_map = {
                'price_asc': 'price ASC',
                'price_desc': 'price DESC',
                'name_asc': 'name ASC',
                'name_desc': 'name DESC',
                'newest': 'created_at DESC',
                'oldest': 'created_at ASC',
            }
            order_clause = sort_map.get(sort_by, 'created_at DESC')
            
            # Pagination
            offset = (page - 1) * page_size
            query += f" ORDER BY {order_clause} LIMIT %s OFFSET %s"
            params.extend([page_size, offset])
            
            await cur.execute(query, params)
            shoes = await cur.fetchall()
            
            # Parse JSON fields
            for shoe in shoes:
                if shoe.get("sizes_available") and isinstance(shoe["sizes_available"], str):
                    try:
                        shoe["sizes_available"] = json.loads(shoe["sizes_available"])
                    except:
                        shoe["sizes_available"] = []
            
            return {
                "items": shoes,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }

async def get_shoe_by_id(shoe_id: int):
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM shoes WHERE id = %s", (shoe_id,))
            shoe = await cur.fetchone()
            if shoe and shoe.get("sizes_available") and isinstance(shoe["sizes_available"], str):
                try:
                    shoe["sizes_available"] = json.loads(shoe["sizes_available"])
                except:
                    shoe["sizes_available"] = []
            return shoe

async def create_shoe(data: dict):
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            sizes_json = json.dumps(data.get("sizes_available", []))
            
            query = """
                INSERT INTO shoes 
                (name, brand, category, price, description, image_filename, stock, sizes_available)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                data["name"], data["brand"], data["category"], data["price"],
                data.get("description", ""), data.get("image_filename"),
                data.get("stock", 0), sizes_json
            )
            
            await cur.execute(query, params)
            await conn.commit()
            return cur.lastrowid

async def update_shoe(shoe_id: int, data: dict):
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            updates = []
            params = []
            
            for key, value in data.items():
                if key == "sizes_available":
                    updates.append("sizes_available = %s")
                    params.append(json.dumps(value))
                elif key != "id":
                    updates.append(f"{key} = %s")
                    params.append(value)
                    
            if not updates:
                return False
                
            query = f"UPDATE shoes SET {', '.join(updates)} WHERE id = %s"
            params.append(shoe_id)
            
            await cur.execute(query, params)
            await conn.commit()
            return cur.rowcount > 0

async def soft_delete_shoe(shoe_id: int):
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE shoes SET is_active = FALSE WHERE id = %s", (shoe_id,))
            await conn.commit()
            return cur.rowcount > 0

async def get_distinct_brands():
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT DISTINCT brand FROM shoes WHERE is_active = TRUE ORDER BY brand")
            res = await cur.fetchall()
            return [r["brand"] for r in res] if res else []

async def get_distinct_categories():
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT DISTINCT category FROM shoes WHERE is_active = TRUE ORDER BY category")
            res = await cur.fetchall()
            return [r["category"] for r in res] if res else []

async def get_price_range():
    """Get the min and max prices from active shoes."""
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT MIN(price) as min_price, MAX(price) as max_price FROM shoes WHERE is_active = TRUE"
            )
            res = await cur.fetchone()
            if res:
                return {
                    "min": float(res["min_price"] or 0),
                    "max": float(res["max_price"] or 0)
                }
            return {"min": 0, "max": 0}
