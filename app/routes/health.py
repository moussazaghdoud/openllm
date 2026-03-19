"""Health and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.models import HealthResponse
from app.storage import get_store

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    redis_status = "disconnected"
    try:
        store = await get_store()
        if await store.ping():
            redis_status = "connected"
    except Exception:
        pass

    presidio_status = "built-in"
    if settings.presidio_external_url:
        presidio_status = f"external ({settings.presidio_external_url})"

    return HealthResponse(
        status="ok",
        version="0.1.0",
        presidio=presidio_status,
        redis=redis_status,
    )
