"""NATS router — forwards requests to on-premise engines via NATS.

When a workspace has deployment_mode='onprem', API requests are not
processed locally. Instead, they are published to NATS and the
on-premise bridge picks them up, forwards to the local engine,
and replies through NATS.

This module manages the NATS connection on the Railway (SaaS) side.
"""

from __future__ import annotations

import json
import logging
import uuid

import nats
from nats.aio.client import Client as NATS

from app.config import settings

logger = logging.getLogger("securellm.nats_router")

_nc: NATS | None = None


async def connect() -> None:
    """Connect to the NATS server."""
    global _nc
    if not settings.nats_enabled:
        logger.info("NATS disabled (nats_enabled=false)")
        return

    try:
        opts = {
            "servers": [settings.nats_url],
            "reconnect_time_wait": 2,
            "max_reconnect_attempts": -1,
        }
        if settings.nats_token:
            opts["token"] = settings.nats_token

        _nc = await nats.connect(**opts)
        logger.info("Connected to NATS at %s", settings.nats_url)
    except Exception as e:
        logger.error("Failed to connect to NATS: %s", e)
        _nc = None


async def close() -> None:
    """Close NATS connection."""
    global _nc
    if _nc:
        await _nc.drain()
        _nc = None
        logger.info("NATS connection closed")


def is_connected() -> bool:
    """Check if NATS is connected."""
    return _nc is not None and _nc.is_connected


async def forward_request(
    workspace_id: str,
    method: str,
    path: str,
    headers: dict[str, str],
    body: str,
) -> dict:
    """Forward an HTTP request to an on-premise engine via NATS.

    Uses NATS request/reply pattern for reliable delivery.

    Args:
        workspace_id: Target workspace
        method: HTTP method (GET, POST, etc.)
        path: Request path (e.g., /v1/anonymize)
        headers: HTTP headers
        body: Request body as string

    Returns:
        dict with keys: status, headers, body
    """
    if not is_connected():
        return {
            "status": 503,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "NATS not connected",
                "detail": "On-premise tunnel is not available",
            }),
        }

    subject = f"securellm.{workspace_id}.request"

    request_msg = {
        "id": uuid.uuid4().hex,
        "method": method,
        "path": path,
        "headers": headers,
        "body": body,
    }

    try:
        reply = await _nc.request(
            subject,
            json.dumps(request_msg).encode(),
            timeout=settings.nats_request_timeout,
        )
        response = json.loads(reply.data.decode())
        return response

    except nats.errors.NoRespondersError:
        logger.error("No on-premise engine connected for workspace %s", workspace_id)
        return {
            "status": 503,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Engine offline",
                "detail": f"No on-premise engine is connected for this workspace. "
                          f"Check that the SecureLLM engine is running on-premise.",
            }),
        }

    except nats.errors.TimeoutError:
        logger.error("Request timeout for workspace %s on %s %s", workspace_id, method, path)
        return {
            "status": 504,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Engine timeout",
                "detail": "On-premise engine did not respond in time",
            }),
        }

    except Exception as e:
        logger.error("NATS request error for workspace %s: %s", workspace_id, e)
        return {
            "status": 502,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Tunnel error",
                "detail": str(e),
            }),
        }


async def check_engine_online(workspace_id: str) -> bool:
    """Check if an on-premise engine is connected for this workspace."""
    if not is_connected():
        return False

    try:
        reply = await _nc.request(
            f"securellm.{workspace_id}.request",
            json.dumps({
                "id": uuid.uuid4().hex,
                "method": "GET",
                "path": "/health",
                "headers": {},
                "body": "",
            }).encode(),
            timeout=5,
        )
        response = json.loads(reply.data.decode())
        return response.get("status") == 200
    except Exception:
        return False
