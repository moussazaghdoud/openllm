"""Pydantic models for API request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Anonymization ────────────────────────────────────────

class AnonymizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    workspace_id: str = Field(..., description="Tenant/workspace identifier")


class AnonymizeResponse(BaseModel):
    anonymized_text: str
    mapping_id: str = Field(..., description="Opaque ID to retrieve the mapping for deanonymization")


class DeanonymizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    mapping_id: str


class DeanonymizeResponse(BaseModel):
    text: str


# ── LLM Proxy (chat completions pass-through) ───────────

class LLMProxyRequest(BaseModel):
    """OpenAI-compatible chat completion request that flows through the privacy gateway."""
    workspace_id: str
    model: str = "default"
    messages: list[dict]
    max_tokens: int = 4096
    temperature: float = 0.7
    stream: bool = False


class LLMProxyResponse(BaseModel):
    choices: list[dict]
    model: str
    usage: dict | None = None


# ── Workspace / Tenant ───────────────────────────────────

class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    ppi_terms: list[str] = Field(default_factory=list, description="Custom proprietary terms to anonymize")


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    ppi_term_count: int
    api_key: str | None = None  # only returned on creation


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    ppi_terms: list[str] | None = None


# ── Health ───────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    presidio: str
    redis: str
