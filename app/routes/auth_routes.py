"""Authentication routes — login, logout, user CRUD."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.auth import (
    COOKIE_NAME,
    authenticate_user,
    create_access_token,
    create_user,
    delete_user,
    get_current_user,
    get_user,
    list_users,
    require_admin_flexible,
    update_user,
)
from app.models import LoginRequest, UserCreate, UserResponse, UserUpdate
from app.storage import KVStore, get_store

router = APIRouter(tags=["auth"])


# ── Login / Logout ────────────────────────────────────────

@router.post("/auth/login")
async def login(body: LoginRequest, store: KVStore = Depends(get_store)):
    user = await authenticate_user(store, body.email, body.password)
    if not user:
        raise HTTPException(401, "Invalid email or password")

    token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"],
        "ws": user.get("workspace_id"),
    })

    resp = JSONResponse({
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "workspace_id": user.get("workspace_id"),
        }
    })
    resp.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        max_age=60 * 480,
        path="/",
    )
    return resp


@router.post("/auth/logout")
async def logout():
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(COOKIE_NAME, path="/")
    return resp


@router.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "workspace_id": user.get("workspace_id"),
    }


# ── User Management (admin only) ─────────────────────────

@router.get("/admin/users", dependencies=[Depends(require_admin_flexible)])
async def admin_list_users(store: KVStore = Depends(get_store)):
    users = await list_users(store)
    return [
        UserResponse(
            id=u["id"],
            email=u["email"],
            role=u["role"],
            workspace_id=u.get("workspace_id"),
            created_at=u.get("created_at", ""),
        )
        for u in users
    ]


@router.post("/admin/users", dependencies=[Depends(require_admin_flexible)])
async def admin_create_user(body: UserCreate, store: KVStore = Depends(get_store)):
    user = await create_user(store, body.email, body.password, body.role, body.workspace_id)
    return UserResponse(
        id=user["id"],
        email=user["email"],
        role=user["role"],
        workspace_id=user.get("workspace_id"),
        created_at=user.get("created_at", ""),
    )


@router.get("/admin/users/{user_id}", dependencies=[Depends(require_admin_flexible)])
async def admin_get_user(user_id: str, store: KVStore = Depends(get_store)):
    user = await get_user(store, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return UserResponse(
        id=user["id"],
        email=user["email"],
        role=user["role"],
        workspace_id=user.get("workspace_id"),
        created_at=user.get("created_at", ""),
    )


@router.patch("/admin/users/{user_id}", dependencies=[Depends(require_admin_flexible)])
async def admin_update_user(user_id: str, body: UserUpdate, store: KVStore = Depends(get_store)):
    user = await update_user(
        store, user_id,
        email=body.email,
        password=body.password,
        role=body.role,
        workspace_id=body.workspace_id,
    )
    if not user:
        raise HTTPException(404, "User not found")
    return UserResponse(
        id=user["id"],
        email=user["email"],
        role=user["role"],
        workspace_id=user.get("workspace_id"),
        created_at=user.get("created_at", ""),
    )


@router.delete("/admin/users/{user_id}", dependencies=[Depends(require_admin_flexible)])
async def admin_delete_user(user_id: str, store: KVStore = Depends(get_store)):
    ok = await delete_user(store, user_id)
    if not ok:
        raise HTTPException(404, "User not found")
    return {"ok": True}
