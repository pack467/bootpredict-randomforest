"""
History Routes
==============
API endpoints for managing prediction history.
"""

from fastapi import APIRouter, Request
from app.controllers.history_controller import (
    handle_get_history,
    handle_delete_history,
    handle_get_stats
)

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("")
async def get_history(request: Request):
    """
    Get the current user's prediction history.
    Returns all past predictions ordered by most recent first.
    """
    return await handle_get_history(request)


@router.delete("/{prediction_id}")
async def delete_history(request: Request, prediction_id: int):
    """
    Delete a specific prediction history entry.
    Only the owning user can delete their own predictions.
    """
    return await handle_delete_history(request, prediction_id)


@router.get("/stats")
async def get_stats(request: Request):
    """
    Get prediction statistics for the current user.
    Includes total prediction count and class distribution.
    """
    return await handle_get_stats(request)
