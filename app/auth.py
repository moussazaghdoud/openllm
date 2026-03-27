"""Authentication — API keys (programmatic) + JWT sessions (web UI)."""

from __future__ import annotations

import hashlib
import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.storage import KVStore, get_store

# ── Password hashing ──────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── API key helpers (unchanged) ───────────────────────────

def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key() -> str:
    return f"slm_{secrets.token_urlsafe(32)}"


# ── JWT helpers ───────────────────────────────────────────

COOKIE_NAME = "slm_session"


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire, "jti": uuid.uuid4().hex[:16]})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


# ── User CRUD (Redis) ────────────────────────────────────

async def create_user(store: KVStore, email: str, password: str, role: str = "user", workspace_id: str | None = None) -> dict:
    email_lower = email.strip().lower()
    existing = await store.get(f"user_email:{email_lower}")
    if existing:
        raise HTTPException(409, "Email already registered")

    user_id = uuid.uuid4().hex[:12]
    user = {
        "id": user_id,
        "email": email_lower,
        "password_hash": hash_password(password),
        "role": role,
        "workspace_id": workspace_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await store.set(f"user:{user_id}", json.dumps(user))
    await store.set(f"user_email:{email_lower}", user_id)
    return user


async def get_user(store: KVStore, user_id: str) -> dict | None:
    raw = await store.get(f"user:{user_id}")
    return json.loads(raw) if raw else None


async def get_user_by_email(store: KVStore, email: str) -> dict | None:
    email_lower = email.strip().lower()
    user_id = await store.get(f"user_email:{email_lower}")
    if not user_id:
        return None
    return await get_user(store, user_id)


async def authenticate_user(store: KVStore, email: str, password: str) -> dict | None:
    user = await get_user_by_email(store, email)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


async def list_users(store: KVStore) -> list[dict]:
    keys = await store.scan_iter("user:*")
    users = []
    for k in keys:
        if k.startswith("user_email:"):
            continue
        raw = await store.get(k)
        if raw:
            u = json.loads(raw)
            users.append(u)
    return users


async def update_user(store: KVStore, user_id: str, **kwargs) -> dict | None:
    user = await get_user(store, user_id)
    if not user:
        return None

    if "email" in kwargs and kwargs["email"]:
        new_email = kwargs["email"].strip().lower()
        if new_email != user["email"]:
            existing = await store.get(f"user_email:{new_email}")
            if existing:
                raise HTTPException(409, "Email already registered")
            await store.delete(f"user_email:{user['email']}")
            await store.set(f"user_email:{new_email}", user_id)
            user["email"] = new_email

    if "password" in kwargs and kwargs["password"]:
        user["password_hash"] = hash_password(kwargs["password"])

    if "role" in kwargs and kwargs["role"]:
        user["role"] = kwargs["role"]

    if "workspace_id" in kwargs:
        user["workspace_id"] = kwargs["workspace_id"]

    await store.set(f"user:{user_id}", json.dumps(user))
    return user


async def delete_user(store: KVStore, user_id: str) -> bool:
    user = await get_user(store, user_id)
    if not user:
        return False
    await store.delete(f"user:{user_id}", f"user_email:{user['email']}")
    return True


# ── Seed admin on startup ────────────────────────────────

async def seed_admin(store: KVStore) -> None:
    existing = await get_user_by_email(store, settings.admin_email)
    if existing:
        return
    await create_user(store, settings.admin_email, settings.admin_password, role="admin")
    import logging
    logging.getLogger("securellm.auth").info("Admin user created: %s", settings.admin_email)


# ── FastAPI dependencies ──────────────────────────────────

async def require_workspace(
    x_api_key: str = Header(..., alias="X-API-Key"),
    store: KVStore = Depends(get_store),
) -> str:
    """Validate API key → return workspace_id. For programmatic REST access."""
    ws_id = await store.get(f"apikey:{hash_key(x_api_key)}")
    if not ws_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")
    return ws_id


async def require_admin(
    x_admin_key: str = Header(..., alias="X-Admin-Key"),
) -> None:
    """Validate admin key for management endpoints (legacy)."""
    if not secrets.compare_digest(x_admin_key, settings.admin_api_key):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid admin key")


def _get_jwt_from_request(request: Request) -> str | None:
    """Extract JWT from cookie or Authorization header."""
    token = request.cookies.get(COOKIE_NAME)
    if token:
        return token
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


async def get_current_user(request: Request, store: KVStore = Depends(get_store)) -> dict:
    """Extract and validate JWT → return user dict."""
    token = _get_jwt_from_request(request)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    user = await get_user(store, user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


async def require_admin_user(user: dict = Depends(get_current_user)) -> dict:
    """Require JWT session with admin role."""
    if user.get("role") != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user


async def require_admin_flexible(request: Request, store: KVStore = Depends(get_store)) -> None:
    """Accept EITHER admin JWT session OR X-Admin-Key header."""
    # Try JWT first
    token = _get_jwt_from_request(request)
    if token:
        try:
            payload = decode_token(token)
            user = await get_user(store, payload.get("sub", ""))
            if user and user.get("role") == "admin":
                return
        except JWTError:
            pass

    # Fall back to admin key
    admin_key = request.headers.get("X-Admin-Key", "")
    if admin_key and secrets.compare_digest(admin_key, settings.admin_api_key):
        return

    raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")


async def require_workspace_flexible(request: Request, store: KVStore = Depends(get_store)) -> str:
    """Accept EITHER JWT session OR X-API-Key header → return workspace_id."""
    # Try JWT first
    token = _get_jwt_from_request(request)
    if token:
        try:
            payload = decode_token(token)
            user = await get_user(store, payload.get("sub", ""))
            if user and user.get("workspace_id"):
                return user["workspace_id"]
        except JWTError:
            pass

    # Fall back to API key
    api_key = request.headers.get("X-API-Key", "")
    if api_key:
        ws_id = await store.get(f"apikey:{hash_key(api_key)}")
        if ws_id:
            return ws_id

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
