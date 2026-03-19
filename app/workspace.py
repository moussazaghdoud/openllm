"""Workspace (tenant) management — CRUD operations."""

from __future__ import annotations

import json
import uuid

import redis.asyncio as aioredis

from app.auth import generate_api_key, hash_key


async def create_workspace(
    redis: aioredis.Redis, name: str, ppi_terms: list[str] | None = None
) -> dict:
    ws_id = uuid.uuid4().hex[:12]
    api_key = generate_api_key()

    ws_data = {"id": ws_id, "name": name}
    await redis.set(f"ws:{ws_id}", json.dumps(ws_data))
    await redis.set(f"apikey:{hash_key(api_key)}", ws_id)

    if ppi_terms:
        await redis.set(f"ws:{ws_id}:ppi_terms", json.dumps(ppi_terms))

    return {"id": ws_id, "name": name, "api_key": api_key, "ppi_term_count": len(ppi_terms or [])}


async def get_workspace(redis: aioredis.Redis, ws_id: str) -> dict | None:
    raw = await redis.get(f"ws:{ws_id}")
    if not raw:
        return None
    ws = json.loads(raw)

    raw_terms = await redis.get(f"ws:{ws_id}:ppi_terms")
    ws["ppi_term_count"] = len(json.loads(raw_terms)) if raw_terms else 0
    return ws


async def update_workspace(
    redis: aioredis.Redis, ws_id: str, name: str | None = None, ppi_terms: list[str] | None = None
) -> dict | None:
    raw = await redis.get(f"ws:{ws_id}")
    if not raw:
        return None

    ws = json.loads(raw)
    if name is not None:
        ws["name"] = name
        await redis.set(f"ws:{ws_id}", json.dumps(ws))

    if ppi_terms is not None:
        await redis.set(f"ws:{ws_id}:ppi_terms", json.dumps(ppi_terms))

    return await get_workspace(redis, ws_id)


async def delete_workspace(redis: aioredis.Redis, ws_id: str) -> bool:
    raw = await redis.get(f"ws:{ws_id}")
    if not raw:
        return False

    # Clean up all workspace keys (scan for ws:{id}:* and map:ws_id:*)
    await redis.delete(f"ws:{ws_id}", f"ws:{ws_id}:ppi_terms")

    # Remove API key mappings (scan)
    cursor = 0
    while True:
        cursor, keys = await redis.scan(cursor, match="apikey:*", count=100)
        for key in keys:
            val = await redis.get(key)
            if val == ws_id:
                await redis.delete(key)
        if cursor == 0:
            break

    return True
