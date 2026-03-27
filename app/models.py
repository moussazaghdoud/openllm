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
    file_ids: list[str] = Field(default_factory=list, description="Attached file IDs to include as context")


class LLMProxyResponse(BaseModel):
    choices: list[dict]
    model: str
    usage: dict | None = None


# ── LLM Configuration ────────────────────────────────────

class LLMConfig(BaseModel):
    provider: str = Field(..., description="anthropic, openai, openclaw, or custom")
    upstream_url: str = Field(..., description="Base URL of the LLM API")
    api_key: str = Field(..., min_length=1, description="API key for the upstream LLM")
    default_model: str = Field("", description="Default model to use (e.g. claude-sonnet-4-20250514)")


class LLMConfigResponse(BaseModel):
    provider: str
    upstream_url: str
    default_model: str
    configured: bool


# ── Workspace / Tenant ───────────────────────────────────

class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    ppi_terms: list[str] = Field(default_factory=list, description="Custom proprietary terms to anonymize")
    llm: LLMConfig | None = Field(None, description="LLM upstream configuration")
    deployment_mode: str = Field("cloud", description="'cloud' (process on Railway) or 'onprem' (route via NATS tunnel)")


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    ppi_term_count: int
    llm: LLMConfigResponse | None = None
    deployment_mode: str = "cloud"
    max_file_size_mb: int = 50
    api_key: str | None = None  # only returned on creation


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    ppi_terms: list[str] | None = None
    llm: LLMConfig | None = None
    deployment_mode: str | None = None
    max_file_size_mb: int | None = None


# ── Portal (Customer-facing) ─────────────────────────────

class PortalWorkspaceInfo(BaseModel):
    id: str
    name: str
    ppi_term_count: int
    llm: LLMConfigResponse | None = None
    deployment_mode: str = "cloud"
    stats: dict = Field(default_factory=lambda: {"anon_count": 0, "last_used": None})


class PPITermsResponse(BaseModel):
    terms: list[str]


class PPITermsUpdate(BaseModel):
    terms: list[str]


class SubKeyCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=64)


class SubKeyResponse(BaseModel):
    label: str
    prefix: str
    created_at: str


class SubKeyCreated(BaseModel):
    label: str
    api_key: str
    created_at: str


# ── Users / Auth ─────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserCreate(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=4)
    role: str = Field("user", description="'admin' or 'user'")
    workspace_id: str | None = Field(None, description="Workspace to link user to (required for role=user)")


class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    role: str | None = None
    workspace_id: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    workspace_id: str | None = None
    created_at: str


# ── Health ───────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    presidio: str
    redis: str
