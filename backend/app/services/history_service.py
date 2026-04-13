"""
History Service
===============
Business logic for managing user prediction history.
Uses centralized MySQL connection pool.
"""

import json
from app.database.connection import get_pool


async def get_user_history(user_id: int):
    """
    Get all prediction history for a specific user.

    Args:
        user_id: The user's database ID

    Returns:
        list: List of prediction history dicts, ordered by most recent first
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """SELECT id, peminatan, brand, posisi, predicted_class,
                          probabilities, feature_importance, explanation, created_at
                   FROM predictions
                   WHERE user_id = %s
                   ORDER BY created_at DESC""",
                (user_id,)
            )
            rows = await cur.fetchall()

            history = []
            for row in rows:
                item = {
                    "id": row["id"],
                    "peminatan": row["peminatan"],
                    "brand": row["brand"],
                    "posisi": row["posisi"],
                    "predicted_class": row["predicted_class"],
                    "probabilities": json.loads(row["probabilities"]) if row["probabilities"] else {},
                    "feature_importance": json.loads(row["feature_importance"]) if row["feature_importance"] else {},
                    "explanation": row["explanation"],
                    "created_at": str(row["created_at"]) if row["created_at"] else None
                }
                history.append(item)

            return history


async def delete_history_item(prediction_id: int, user_id: int):
    """
    Delete a specific prediction history entry.
    Only allows deletion by the owning user.

    Args:
        prediction_id: ID of the prediction to delete
        user_id: ID of the requesting user (for ownership check)

    Returns:
        dict: Result with success status
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Check ownership
            await cur.execute(
                "SELECT id FROM predictions WHERE id = %s AND user_id = %s",
                (prediction_id, user_id)
            )
            exists = await cur.fetchone()

            if not exists:
                return {"success": False, "message": "Data tidak ditemukan atau bukan milik Anda"}

            await cur.execute("DELETE FROM predictions WHERE id = %s", (prediction_id,))
        await conn.commit()

        return {"success": True, "message": "Riwayat berhasil dihapus"}


async def get_user_stats(user_id: int):
    """
    Get prediction statistics for a user.

    Args:
        user_id: User's database ID

    Returns:
        dict: Statistics including total predictions and class distribution
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Total predictions
            await cur.execute(
                "SELECT COUNT(*) as total FROM predictions WHERE user_id = %s",
                (user_id,)
            )
            row = await cur.fetchone()
            total = row["total"]

            # Class distribution
            await cur.execute(
                """SELECT predicted_class, COUNT(*) as count
                   FROM predictions WHERE user_id = %s
                   GROUP BY predicted_class""",
                (user_id,)
            )
            rows = await cur.fetchall()
            distribution = {row["predicted_class"]: row["count"] for row in rows}

            return {
                "total_predictions": total,
                "class_distribution": distribution
            }
