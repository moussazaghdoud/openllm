"""Health and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.models import HealthResponse
from app.redis_client import get_redis

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    # Redis check
    redis_status = "disconnected"
    try:
        redis = await get_redis()
        await redis.ping()
        redis_status = "connected"
    except Exception:
        pass

    # Presidio check
    presidio_status = "built-in"
    if settings.presidio_external_url:
        presidio_status = f"external ({settings.presidio_external_url})"

    return HealthResponse(
        status="ok" if redis_status == "connected" else "degraded",
        version="0.1.0",
        presidio=presidio_status,
        redis=redis_status,
    )
