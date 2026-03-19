"""Privacy Gateway endpoints — anonymize / deanonymize / LLM proxy."""

from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_workspace
from app.config import settings
from app.engine.pipeline import PrivacyPipeline
from app.models import (
    AnonymizeRequest,
    AnonymizeResponse,
    DeanonymizeRequest,
    DeanonymizeResponse,
    LLMProxyRequest,
    LLMProxyResponse,
)
from app.storage import KVStore, get_store

logger = logging.getLogger("securellm.routes.anonymize")

router = APIRouter(prefix="/v1", tags=["privacy-gateway"])


@router.post("/anonymize", response_model=AnonymizeResponse)
async def anonymize(
    req: AnonymizeRequest,
    workspace_id: str = Depends(require_workspace),
    store: KVStore = Depends(get_store),
):
    if req.workspace_id != workspace_id:
        raise HTTPException(403, "Workspace ID mismatch")

    pipeline = await PrivacyPipeline.for_workspace(store, workspace_id)
    anonymized_text, mapping_id = await pipeline.anonymize(req.text)

    return AnonymizeResponse(anonymized_text=anonymized_text, mapping_id=mapping_id)


@router.post("/deanonymize", response_model=DeanonymizeResponse)
async def deanonymize(
    req: DeanonymizeRequest,
    workspace_id: str = Depends(require_workspace),
    store: KVStore = Depends(get_store),
):
    if not req.mapping_id.startswith(f"map:{workspace_id}:"):
        raise HTTPException(403, "Mapping does not belong to this workspace")

    pipeline = await PrivacyPipeline.for_workspace(store, workspace_id)
    text = await pipeline.deanonymize(req.text, req.mapping_id)

    return DeanonymizeResponse(text=text)


@router.post("/chat/completions", response_model=LLMProxyResponse)
async def llm_proxy(
    req: LLMProxyRequest,
    workspace_id: str = Depends(require_workspace),
    store: KVStore = Depends(get_store),
):
    """Privacy-first LLM proxy — anonymize -> LLM -> deanonymize."""
    if req.workspace_id != workspace_id:
        raise HTTPException(403, "Workspace ID mismatch")

    if not settings.llm_upstream_url:
        raise HTTPException(503, "LLM upstream not configured")

    pipeline = await PrivacyPipeline.for_workspace(store, workspace_id)

    # Step 1: Anonymize user/system messages
    anonymized_messages = []
    mapping_ids: list[str] = []

    for msg in req.messages:
        content = msg.get("content", "")
        if not content or msg.get("role") == "assistant":
            anonymized_messages.append(msg)
            continue

        anon_text, mapping_id = await pipeline.anonymize(content)
        mapping_ids.append(mapping_id)
        anonymized_messages.append({**msg, "content": anon_text})

    # Step 2: Forward to upstream LLM
    upstream_payload = {
        "model": req.model,
        "messages": anonymized_messages,
        "max_tokens": req.max_tokens,
        "temperature": req.temperature,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{settings.llm_upstream_url.rstrip('/')}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_upstream_api_key}",
                    "Content-Type": "application/json",
                },
                json=upstream_payload,
            )
            resp.raise_for_status()
            llm_data = resp.json()
    except httpx.HTTPError as e:
        logger.error("LLM upstream error: %s", e)
        raise HTTPException(502, f"LLM upstream error: {e}")

    # Step 3: Deanonymize response
    choices = llm_data.get("choices", [])
    for choice in choices:
        content = choice.get("message", {}).get("content", "")
        if content:
            for mid in mapping_ids:
                content = await pipeline.deanonymize(content, mid)
            choice["message"]["content"] = content

    return LLMProxyResponse(
        choices=choices,
        model=llm_data.get("model", req.model),
        usage=llm_data.get("usage"),
    )
