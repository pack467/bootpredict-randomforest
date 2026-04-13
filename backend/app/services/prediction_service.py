"""
Prediction Service
==================
Business logic for making predictions and getting product recommendations.
Uses centralized MySQL connection pool.
Includes relevance scoring to sort recommendations by best match.
"""

import json
import os
from app.ml.predict import predict as ml_predict
from app.config import PRODUCT_CATALOG_PATH, VALID_PEMINATAN, VALID_BRAND, VALID_POSISI
from app.database.connection import get_pool


def validate_input(peminatan: str, brand: str, posisi: str):
    """
    Validate prediction input values.

    Args:
        peminatan: Play style preference
        brand: Preferred brand
        posisi: Player position

    Returns:
        tuple: (is_valid, error_message)
    """
    errors = []

    if peminatan.lower() not in VALID_PEMINATAN:
        errors.append(f"Peminatan '{peminatan}' tidak valid. Pilihan: {', '.join(VALID_PEMINATAN)}")

    if brand.lower() not in VALID_BRAND:
        errors.append(f"Brand '{brand}' tidak valid. Pilihan: {', '.join(VALID_BRAND)}")

    if posisi.lower() not in VALID_POSISI:
        errors.append(f"Posisi '{posisi}' tidak valid. Pilihan: {', '.join(VALID_POSISI)}")

    if errors:
        return False, "; ".join(errors)

    return True, None


def calculate_match_score(product_stats: dict, predicted_class: str, peminatan: str, posisi: str):
    """
    Calculate a relevance/match score for a product based on user criteria.
    Higher score = better match.

    Scoring factors:
    1. Primary stat alignment with predicted class (e.g., speed_boot → speed stat)
    2. Playing style (peminatan) alignment with stats
    3. Position-specific stat preferences
    4. Overall stat balance

    Args:
        product_stats: Dict with speed, control, power, touch, weight, durability
        predicted_class: The predicted boot category
        peminatan: User's play style preference
        posisi: User's playing position

    Returns:
        float: Match score (0-100)
    """
    if not product_stats:
        return 50.0  # Default neutral score

    speed = product_stats.get("speed", 50)
    control = product_stats.get("control", 50)
    power = product_stats.get("power", 50)
    touch = product_stats.get("touch", 50)
    weight = product_stats.get("weight", 50)
    durability = product_stats.get("durability", 50)

    score = 0.0

    # === Factor 1: Primary class stat alignment (weight: 40%) ===
    class_stat_weights = {
        "speed_boot": {"speed": 0.35, "weight": 0.25, "control": 0.10, "touch": 0.10, "power": 0.10, "durability": 0.10},
        "control_boot": {"control": 0.30, "touch": 0.25, "speed": 0.10, "power": 0.10, "weight": 0.10, "durability": 0.15},
        "power_boot": {"power": 0.35, "durability": 0.20, "control": 0.15, "touch": 0.10, "speed": 0.10, "weight": 0.10}
    }

    weights = class_stat_weights.get(predicted_class, class_stat_weights["speed_boot"])
    class_score = (
        speed * weights["speed"] +
        control * weights["control"] +
        power * weights["power"] +
        touch * weights["touch"] +
        weight * weights["weight"] +
        durability * weights["durability"]
    )
    score += class_score * 0.40

    # === Factor 2: Playing style (peminatan) alignment (weight: 30%) ===
    peminatan_weights = {
        "speed": {"speed": 0.40, "weight": 0.30, "control": 0.10, "touch": 0.10, "power": 0.05, "durability": 0.05},
        "control": {"control": 0.35, "touch": 0.30, "speed": 0.10, "power": 0.05, "weight": 0.10, "durability": 0.10},
        "power": {"power": 0.40, "durability": 0.20, "control": 0.15, "touch": 0.10, "speed": 0.10, "weight": 0.05}
    }

    pem_weights = peminatan_weights.get(peminatan.lower(), peminatan_weights["speed"])
    peminatan_score = (
        speed * pem_weights["speed"] +
        control * pem_weights["control"] +
        power * pem_weights["power"] +
        touch * pem_weights["touch"] +
        weight * pem_weights["weight"] +
        durability * pem_weights["durability"]
    )
    score += peminatan_score * 0.30

    # === Factor 3: Position-specific preferences (weight: 20%) ===
    position_weights = {
        "striker": {"speed": 0.25, "power": 0.30, "touch": 0.15, "control": 0.10, "weight": 0.10, "durability": 0.10},
        "midfielder": {"control": 0.30, "touch": 0.25, "speed": 0.15, "power": 0.10, "durability": 0.10, "weight": 0.10},
        "defender": {"durability": 0.30, "power": 0.25, "control": 0.20, "speed": 0.10, "touch": 0.10, "weight": 0.05},
        "goalkeeper": {"durability": 0.25, "control": 0.25, "touch": 0.20, "power": 0.15, "speed": 0.10, "weight": 0.05}
    }

    pos_weights = position_weights.get(posisi.lower(), position_weights["midfielder"])
    position_score = (
        speed * pos_weights["speed"] +
        control * pos_weights["control"] +
        power * pos_weights["power"] +
        touch * pos_weights["touch"] +
        weight * pos_weights["weight"] +
        durability * pos_weights["durability"]
    )
    score += position_score * 0.20

    # === Factor 4: Overall stat quality bonus (weight: 10%) ===
    avg_stat = (speed + control + power + touch + weight + durability) / 6
    score += avg_stat * 0.10

    return round(score, 1)


def get_recommended_products(predicted_class: str, brand: str, peminatan: str = "", posisi: str = ""):
    """
    Get product recommendations based on predicted class, brand, and user criteria.
    Returns specific shoe models with stats, images, and brand info.
    Products are SORTED by match score (most suitable first).

    Strategy:
    - Show ALL shoes from the user's preferred brand for the predicted class
    - Add top shoes from each OTHER brand for variety
    - Sort each group by match_score (highest first)

    Args:
        predicted_class: The predicted boot category (e.g., "speed_boot")
        brand: The user's preferred brand
        peminatan: The user's play style preference
        posisi: The user's playing position

    Returns:
        list: List of recommended product dicts with stats, images, and match_score
    """
    if not os.path.exists(PRODUCT_CATALOG_PATH):
        return []

    with open(PRODUCT_CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    products = []
    brand_lower = brand.lower()

    # 1. Get ALL products from the user's preferred brand for the predicted class
    if predicted_class in catalog:
        if brand_lower in catalog[predicted_class]:
            for product in catalog[predicted_class][brand_lower]:
                product_entry = product.copy()
                product_entry["brand"] = product.get("brand", brand.title())
                product_entry["is_primary"] = True  # Flag as primary recommendation
                # Calculate match score
                product_entry["match_score"] = calculate_match_score(
                    product.get("stats", {}), predicted_class, peminatan, posisi
                )
                products.append(product_entry)

    # 2. Add top shoes from each other brand for variety (up to 2 per brand)
    if predicted_class in catalog:
        for other_brand, brand_products in catalog[predicted_class].items():
            if other_brand != brand_lower and brand_products:
                # Score all products from other brands
                scored_products = []
                for product in brand_products:
                    product_entry = product.copy()
                    product_entry["brand"] = product_entry.get("brand", other_brand.title())
                    product_entry["is_primary"] = False
                    product_entry["match_score"] = calculate_match_score(
                        product.get("stats", {}), predicted_class, peminatan, posisi
                    )
                    scored_products.append(product_entry)

                # Sort by score and take top 2
                scored_products.sort(key=lambda x: x["match_score"], reverse=True)
                products.extend(scored_products[:2])

    # 3. Sort primary products by match_score (highest first)
    primary = [p for p in products if p["is_primary"]]
    secondary = [p for p in products if not p["is_primary"]]

    primary.sort(key=lambda x: x["match_score"], reverse=True)
    secondary.sort(key=lambda x: x["match_score"], reverse=True)

    # Add rank labels
    for i, p in enumerate(primary):
        p["rank"] = i + 1
    for i, p in enumerate(secondary):
        p["rank"] = i + 1

    return primary + secondary


async def make_prediction(user_id: int, peminatan: str, brand: str, posisi: str):
    """
    Make a prediction and save it to the database.

    Args:
        user_id: ID of the user making the prediction
        peminatan: Play style preference
        brand: Preferred brand
        posisi: Player position

    Returns:
        dict: Complete prediction results with recommendations
    """
    # Validate input
    is_valid, error = validate_input(peminatan, brand, posisi)
    if not is_valid:
        return {"success": False, "message": error}

    try:
        # Get ML prediction
        result = ml_predict(
            peminatan=peminatan.lower(),
            brand=brand.lower(),
            posisi=posisi.lower()
        )

        # Get product recommendations (pass peminatan and posisi for scoring)
        products = get_recommended_products(
            result["predicted_class"], brand,
            peminatan=peminatan, posisi=posisi
        )
        result["recommended_products"] = products

        # Save to database
        pool = get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """INSERT INTO predictions
                       (user_id, peminatan, brand, posisi, predicted_class,
                        probabilities, feature_importance, explanation)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        user_id,
                        peminatan.lower(),
                        brand.lower(),
                        posisi.lower(),
                        result["predicted_class"],
                        json.dumps(result["probabilities"]),
                        json.dumps(result["feature_importance"]),
                        result["explanation"]
                    )
                )
            await conn.commit()

        return {"success": True, "data": result}

    except FileNotFoundError as e:
        return {
            "success": False,
            "message": f"Model belum dilatih. Silakan minta admin untuk melatih model terlebih dahulu. Error: {str(e)}"
        }
    except Exception as e:
        return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}
