"""Document translation endpoint — translate uploaded documents while preserving layout."""

from __future__ import annotations

import base64
import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from fastapi import Request as FastAPIRequest

from app.auth import require_workspace
from app.engine.translator import (
    call_translation,
    extract_docx_paragraphs, rebuild_docx,
    extract_pptx_paragraphs, rebuild_pptx,
    extract_pdf_paragraphs, build_docx_from_paragraphs,
)
from app.storage import KVStore, get_store
from app import workspace as ws_ops
from app import nats_router

logger = logging.getLogger("securellm.translate")

router = APIRouter(prefix="/v1", tags=["translation"])

# TTL for translated files: 24 hours
TRANSLATED_FILE_TTL = 86400


class TranslateRequest(BaseModel):
    file_id: str = Field(..., description="File ID from /v1/upload")
    language: str = Field(..., description="Target language (e.g. French, Spanish, Arabic)")


class TranslateResponse(BaseModel):
    filename: str
    download_id: str
    download_url: str
    paragraphs_translated: int


@router.post("/translate", response_model=TranslateResponse)
async def translate_document(
    req: TranslateRequest,
    request: FastAPIRequest,
    workspace_id: str = Depends(require_workspace),
    store: KVStore = Depends(get_store),
):
    """Translate an uploaded document while preserving its layout.

    - DOCX: text replaced in-place, images/styles/formatting preserved
    - PPTX: text replaced per-slide, shapes/images/animations preserved
    - PDF: text extracted, translated, output as DOCX (PDFs can't be rebuilt)
    """
    # Route to on-premise engine for on-prem workspaces
    mode = await ws_ops.get_deployment_mode(store, workspace_id)
    if mode == "onprem":
        try:
            headers = {k: v for k, v in request.headers.items()
                       if k.lower() not in ("host", "connection", "transfer-encoding", "content-length")}
            resp = await nats_router.forward_request(
                workspace_id=workspace_id,
                method="POST",
                path="/v1/translate",
                headers=headers,
                body=req.model_dump_json(),
            )
            if resp["status"] != 200:
                detail = resp.get("body", "Translation failed")
                try:
                    detail = json.loads(detail)
                except Exception:
                    pass
                raise HTTPException(resp["status"], detail)
            data = json.loads(resp["body"])

            # The translated file is stored in local Redis — fetch it and cache here
            dl_id = data.get("download_id", "")
            if dl_id:
                dl_resp = await nats_router.forward_request(
                    workspace_id=workspace_id,
                    method="GET",
                    path=f"/v1/download-raw/{dl_id}",
                    headers=headers,
                    body="",
                )
                if dl_resp["status"] == 200:
                    # The body comes double-encoded from bridge — unwrap
                    dl_body = dl_resp["body"]
                    try:
                        # Bridge wraps response in json.dumps, so body is a JSON string
                        parsed = json.loads(dl_body)
                        if isinstance(parsed, str):
                            # Double-encoded: json.dumps(json.dumps(data))
                            dl_body = parsed
                        elif isinstance(parsed, dict) and "content" in parsed:
                            # Already a dict — re-serialize for storage
                            dl_body = json.dumps(parsed)
                    except (json.JSONDecodeError, TypeError):
                        pass
                    await store.set(dl_id, dl_body, ex=86400)
                    logger.info("Cached translated file from on-prem: %s", dl_id)

            return TranslateResponse(**data)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("On-prem translate error: %s", e)
            raise HTTPException(502, f"On-premise translation error: {str(e)}")

    if not req.file_id.startswith(f"file:{workspace_id}:"):
        raise HTTPException(403, "File does not belong to this workspace")

    # Get the original file bytes from storage
    raw_file = await store.get(f"{req.file_id}:raw")
    if not raw_file:
        raise HTTPException(404, "Original file not found or expired. Please re-upload.")

    file_meta_raw = await store.get(req.file_id)
    if not file_meta_raw:
        raise HTTPException(404, "File metadata not found")

    file_meta = json.loads(file_meta_raw)
    filename = file_meta["filename"]
    file_bytes = base64.b64decode(raw_file)

    # Get LLM config for translation
    llm_config = await ws_ops.get_llm_config(store, workspace_id)
    if not llm_config:
        raise HTTPException(503, "LLM not configured. Translation requires an LLM.")

    name_lower = filename.lower()

    # Extract, translate, rebuild based on file type
    if name_lower.endswith(".docx"):
        paragraphs = extract_docx_paragraphs(file_bytes)
        if not paragraphs:
            raise HTTPException(422, "No text content found in document")

        translated = await call_translation(paragraphs, req.language, llm_config)
        if not translated:
            raise HTTPException(502, "Translation failed. Please try again.")

        result_bytes = rebuild_docx(file_bytes, translated)
        out_name = filename.rsplit(".", 1)[0] + f"_translated_{req.language}.docx"
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    elif name_lower.endswith((".pptx", ".ppt")):
        paragraphs = extract_pptx_paragraphs(file_bytes)
        if not paragraphs:
            raise HTTPException(422, "No text content found in presentation")

        translated = await call_translation(paragraphs, req.language, llm_config)
        if not translated:
            raise HTTPException(502, "Translation failed. Please try again.")

        result_bytes = rebuild_pptx(file_bytes, translated)
        out_name = filename.rsplit(".", 1)[0] + f"_translated_{req.language}.pptx"
        mime = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

    elif name_lower.endswith(".pdf"):
        paragraphs = extract_pdf_paragraphs(file_bytes)
        if not paragraphs:
            raise HTTPException(422, "No text content found in PDF")

        translated = await call_translation(paragraphs, req.language, llm_config)
        if not translated:
            raise HTTPException(502, "Translation failed. Please try again.")

        result_bytes = build_docx_from_paragraphs(translated)
        out_name = filename.rsplit(".", 1)[0] + f"_translated_{req.language}.docx"
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    else:
        raise HTTPException(415, f"Translation not supported for {filename}. Supported: DOCX, PPTX, PDF")

    # Store translated file for download
    dl_id = f"dl:{workspace_id}:{uuid.uuid4().hex[:10]}"
    dl_data = {
        "filename": out_name,
        "mime": mime,
        "content": base64.b64encode(result_bytes).decode(),
    }
    await store.set(dl_id, json.dumps(dl_data), ex=TRANSLATED_FILE_TTL)

    download_url = f"/v1/download/{dl_id}"
    logger.info("Translation complete: %s -> %s (%d paragraphs, %d bytes)",
                filename, out_name, len(translated), len(result_bytes))

    return TranslateResponse(
        filename=out_name,
        download_id=dl_id,
        download_url=download_url,
        paragraphs_translated=len(translated),
    )


@router.get("/download/{dl_id:path}")
async def download_file(
    dl_id: str,
    store: KVStore = Depends(get_store),
):
    """Download a translated document."""
    raw = await store.get(dl_id)
    if not raw:
        raise HTTPException(404, "File not found or expired")

    data = json.loads(raw)
    content = base64.b64decode(data["content"])

    return Response(
        content=content,
        media_type=data["mime"],
        headers={
            "Content-Disposition": f'attachment; filename="{data["filename"]}"',
            "Content-Length": str(len(content)),
        },
    )


@router.get("/download-raw/{dl_id:path}")
async def download_file_raw(
    dl_id: str,
    store: KVStore = Depends(get_store),
):
    """Return translated file as JSON (for NATS bridge transfer)."""
    raw = await store.get(dl_id)
    if not raw:
        raise HTTPException(404, "File not found or expired")
    # Return the raw JSON string directly — it contains {content, mime, filename}
    return json.loads(raw)


# ── Async Translation (background job) ──────────────────

@router.post("/translate/async")
async def translate_async(
    req: TranslateRequest,
    workspace_id: str = Depends(require_workspace),
    store: KVStore = Depends(get_store),
):
    """Start a translation as a background job. Returns job_id to poll for status.

    Use this for large documents that would timeout on /v1/translate.
    """
    from app.engine.jobs import create_job, run_in_background

    if not req.file_id.startswith(f"file:{workspace_id}:"):
        raise HTTPException(403, "File does not belong to this workspace")

    raw_file = await store.get(f"{req.file_id}:raw")
    if not raw_file:
        raise HTTPException(404, "Original file not found or expired")

    file_meta_raw = await store.get(req.file_id)
    if not file_meta_raw:
        raise HTTPException(404, "File metadata not found")

    llm_config = await ws_ops.get_llm_config(store, workspace_id)
    if not llm_config:
        raise HTTPException(503, "LLM not configured")

    job_id = await create_job(store, workspace_id, "translate", {
        "file_id": req.file_id,
        "language": req.language,
    })

    async def do_translate():
        from app.engine.jobs import update_job
        file_meta = json.loads(file_meta_raw)
        filename = file_meta["filename"]
        file_bytes = base64.b64decode(raw_file)
        name_lower = filename.lower()

        if name_lower.endswith(".docx"):
            paragraphs = extract_docx_paragraphs(file_bytes)
            await update_job(store, job_id, progress=10)
            translated = await call_translation(paragraphs, req.language, llm_config)
            if not translated:
                raise Exception("Translation failed")
            await update_job(store, job_id, progress=80)
            result_bytes = rebuild_docx(file_bytes, translated)
            out_name = filename.rsplit(".", 1)[0] + f"_translated_{req.language}.docx"
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif name_lower.endswith((".pptx", ".ppt")):
            paragraphs = extract_pptx_paragraphs(file_bytes)
            await update_job(store, job_id, progress=10)
            translated = await call_translation(paragraphs, req.language, llm_config)
            if not translated:
                raise Exception("Translation failed")
            await update_job(store, job_id, progress=80)
            result_bytes = rebuild_pptx(file_bytes, translated)
            out_name = filename.rsplit(".", 1)[0] + f"_translated_{req.language}.pptx"
            mime = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif name_lower.endswith(".pdf"):
            paragraphs = extract_pdf_paragraphs(file_bytes)
            await update_job(store, job_id, progress=10)
            translated = await call_translation(paragraphs, req.language, llm_config)
            if not translated:
                raise Exception("Translation failed")
            await update_job(store, job_id, progress=80)
            result_bytes = build_docx_from_paragraphs(translated)
            out_name = filename.rsplit(".", 1)[0] + f"_translated_{req.language}.docx"
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            raise Exception(f"Unsupported file type: {filename}")

        dl_id = f"dl:{workspace_id}:{uuid.uuid4().hex[:10]}"
        dl_data = {"filename": out_name, "mime": mime, "content": base64.b64encode(result_bytes).decode()}
        await store.set(dl_id, json.dumps(dl_data), ex=TRANSLATED_FILE_TTL)

        return {"filename": out_name, "download_id": dl_id, "download_url": f"/v1/download/{dl_id}", "paragraphs_translated": len(translated)}

    run_in_background(store, job_id, do_translate())

    return {"job_id": job_id, "status": "pending"}


@router.get("/jobs/{job_id:path}")
async def get_job_status(
    job_id: str,
    workspace_id: str = Depends(require_workspace),
    store: KVStore = Depends(get_store),
):
    """Poll job status. Returns status, progress, and result when done."""
    if not job_id.startswith(f"job:{workspace_id}:"):
        raise HTTPException(403, "Job does not belong to this workspace")

    from app.engine.jobs import get_job
    job = await get_job(store, job_id)
    if not job:
        raise HTTPException(404, "Job not found or expired")

    return {
        "job_id": job["id"],
        "status": job["status"],
        "progress": job["progress"],
        "result": job["result"],
        "error": job["error"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
    }
