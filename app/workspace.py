"""Workspace (tenant) management — CRUD operations."""

from __future__ import annotations

import json
import uuid

from app.auth import generate_api_key, hash_key
from app.storage import KVStore


async def create_workspace(
    store: KVStore, name: str, ppi_terms: list[str] | None = None, llm: dict | None = None
) -> dict:
    ws_id = uuid.uuid4().hex[:12]
    api_key = generate_api_key()

    ws_data = {"id": ws_id, "name": name}
    await store.set(f"ws:{ws_id}", json.dumps(ws_data))
    await store.set(f"apikey:{hash_key(api_key)}", ws_id)

    if ppi_terms:
        await store.set(f"ws:{ws_id}:ppi_terms", json.dumps(ppi_terms))

    if llm:
        await store.set(f"ws:{ws_id}:llm", json.dumps(llm))

    result = await get_workspace(store, ws_id)
    result["api_key"] = api_key
    return result


async def get_workspace(store: KVStore, ws_id: str) -> dict | None:
    raw = await store.get(f"ws:{ws_id}")
    if not raw:
        return None
    ws = json.loads(raw)

    raw_terms = await store.get(f"ws:{ws_id}:ppi_terms")
    ws["ppi_term_count"] = len(json.loads(raw_terms)) if raw_terms else 0

    raw_llm = await store.get(f"ws:{ws_id}:llm")
    if raw_llm:
        llm = json.loads(raw_llm)
        ws["llm"] = {
            "provider": llm["provider"],
            "upstream_url": llm["upstream_url"],
            "default_model": llm.get("default_model", ""),
            "configured": True,
        }
    else:
        ws["llm"] = None

    return ws


async def get_llm_config(store: KVStore, ws_id: str) -> dict | None:
    """Get raw LLM config including the API key (internal use only)."""
    raw = await store.get(f"ws:{ws_id}:llm")
    if not raw:
        return None
    return json.loads(raw)


async def update_workspace(
    store: KVStore, ws_id: str, name: str | None = None,
    ppi_terms: list[str] | None = None, llm: dict | None = None
) -> dict | None:
    raw = await store.get(f"ws:{ws_id}")
    if not raw:
        return None

    ws = json.loads(raw)
    if name is not None:
        ws["name"] = name
        await store.set(f"ws:{ws_id}", json.dumps(ws))

    if ppi_terms is not None:
        await store.set(f"ws:{ws_id}:ppi_terms", json.dumps(ppi_terms))

    if llm is not None:
        await store.set(f"ws:{ws_id}:llm", json.dumps(llm))

    return await get_workspace(store, ws_id)


async def delete_workspace(store: KVStore, ws_id: str) -> bool:
    raw = await store.get(f"ws:{ws_id}")
    if not raw:
        return False

    await store.delete(f"ws:{ws_id}", f"ws:{ws_id}:ppi_terms", f"ws:{ws_id}:llm")

    keys = await store.scan_iter("apikey:*")
    for key in keys:
        val = await store.get(key)
        if val == ws_id:
            await store.delete(key)

    return True
