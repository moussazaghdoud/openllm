"""Workspace management endpoints (admin-only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

import redis.asyncio as aioredis

from app.auth import require_admin
from app.models import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from app.redis_client import get_redis
from app import workspace as ws_ops

router = APIRouter(prefix="/admin/workspaces", tags=["admin"])


@router.post("", response_model=WorkspaceResponse, dependencies=[Depends(require_admin)])
async def create_workspace(
    body: WorkspaceCreate,
    redis: aioredis.Redis = Depends(get_redis),
):
    result = await ws_ops.create_workspace(redis, body.name, body.ppi_terms)
    return WorkspaceResponse(**result)


@router.get("/{ws_id}", response_model=WorkspaceResponse, dependencies=[Depends(require_admin)])
async def get_workspace(
    ws_id: str,
    redis: aioredis.Redis = Depends(get_redis),
):
    ws = await ws_ops.get_workspace(redis, ws_id)
    if not ws:
        raise HTTPException(404, "Workspace not found")
    return WorkspaceResponse(**ws)


@router.patch("/{ws_id}", response_model=WorkspaceResponse, dependencies=[Depends(require_admin)])
async def update_workspace(
    ws_id: str,
    body: WorkspaceUpdate,
    redis: aioredis.Redis = Depends(get_redis),
):
    ws = await ws_ops.update_workspace(redis, ws_id, body.name, body.ppi_terms)
    if not ws:
        raise HTTPException(404, "Workspace not found")
    return WorkspaceResponse(**ws)


@router.delete("/{ws_id}", dependencies=[Depends(require_admin)])
async def delete_workspace(
    ws_id: str,
    redis: aioredis.Redis = Depends(get_redis),
):
    ok = await ws_ops.delete_workspace(redis, ws_id)
    if not ok:
        raise HTTPException(404, "Workspace not found")
    return {"deleted": True}
