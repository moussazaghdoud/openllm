"""SecureLLM On-Premise — Production-grade single-command startup.

Starts the engine and bridge together. Persists workspace config to disk.
Handles restarts, reconnections, and LLM configuration automatically.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
import signal

if sys.platform == 'win32':
    os.environ['PYTHONUTF8'] = '1'

import httpx
import nats

# ============================================================
# CONFIGURATION — edit this or use environment variables
# ============================================================
NATS_URL = os.environ.get("NATS_URL", "wss://nats-production-a078.up.railway.app")
NATS_TOKEN = os.environ.get("NATS_TOKEN", "38aac21fcf6a21a16073fdfb9919d30141be4f309d7d5402314939fbb9429b5")
WORKSPACE_ID = os.environ.get("WORKSPACE_ID", "f61184f2a76a")
ENGINE_PORT = int(os.environ.get("ENGINE_PORT", "8000"))
ENGINE_URL = f"http://127.0.0.1:{ENGINE_PORT}"
ADMIN_KEY = os.environ.get("ADMIN_KEY", "change-me-admin")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), ".onprem_config.json")


def safe_print(msg):
    try:
        sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()
    except Exception:
        pass


# ============================================================
# PERSISTENT CONFIG — survives restarts
# ============================================================
def load_config() -> dict:
    """Load saved config from disk."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(config: dict):
    """Save config to disk."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        safe_print(f"Warning: could not save config: {e}")


# ============================================================
# ENGINE MANAGEMENT
# ============================================================
engine_process = None


def start_engine():
    """Start the securellm engine as a subprocess."""
    global engine_process
    safe_print(f"Starting engine on port {ENGINE_PORT}...")
    engine_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--port", str(ENGINE_PORT), "--host", "127.0.0.1",
         "--log-level", "info"],
        cwd=os.path.dirname(__file__),
    )
    safe_print(f"Engine started (PID: {engine_process.pid})")


def stop_engine():
    """Stop the engine subprocess."""
    global engine_process
    if engine_process:
        safe_print("Stopping engine...")
        engine_process.terminate()
        try:
            engine_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            engine_process.kill()
        engine_process = None


# ============================================================
# WORKSPACE SETUP
# ============================================================
async def setup_workspace(http: httpx.AsyncClient) -> tuple[str, str]:
    """Find or create workspace, restore LLM config. Returns (ws_id, api_key)."""
    config = load_config()
    ws_name = f"onprem-{WORKSPACE_ID}"

    # Try to find existing workspace
    r = await http.get("/admin/workspaces", headers={"X-Admin-Key": ADMIN_KEY})
    if r.status_code == 200:
        for ws in r.json():
            if ws["name"] == ws_name:
                ws_id = ws["id"]
                safe_print(f"Found existing workspace: {ws_id}")

                # Check if we have a saved API key that still works
                saved_key = config.get("api_key", "")
                if saved_key:
                    test = await http.get("/portal/api/workspace", headers={"X-API-Key": saved_key})
                    if test.status_code == 200:
                        safe_print("Saved API key is valid")
                        # Restore LLM config if needed
                        await restore_llm_config(http, ws_id, config)
                        return ws_id, saved_key
                    safe_print("Saved API key expired, creating new one")

                # Need a new API key — delete and recreate workspace
                await http.delete(f"/admin/workspaces/{ws_id}", headers={"X-Admin-Key": ADMIN_KEY})
                safe_print("Deleted old workspace (key lost)")
                break

    # Create new workspace
    r = await http.post(
        "/admin/workspaces",
        headers={"X-Admin-Key": ADMIN_KEY, "Content-Type": "application/json"},
        json={"name": ws_name},
    )
    if r.status_code != 200:
        safe_print(f"Failed to create workspace: {r.text}")
        sys.exit(1)

    data = r.json()
    ws_id = data["id"]
    api_key = data["api_key"]
    safe_print(f"Created workspace: {ws_id}")

    # Save to disk
    config["workspace_id"] = ws_id
    config["api_key"] = api_key
    save_config(config)

    # Restore LLM config
    await restore_llm_config(http, ws_id, config)

    return ws_id, api_key


async def restore_llm_config(http: httpx.AsyncClient, ws_id: str, config: dict):
    """Restore LLM configuration from saved config."""
    llm = config.get("llm")
    if not llm:
        return

    # Check if already configured
    r = await http.get(
        f"/admin/workspaces/{ws_id}/llm",
        headers={"X-Admin-Key": ADMIN_KEY},
    )
    if r.status_code == 200:
        safe_print("LLM already configured")
        return

    # Restore saved LLM config
    r = await http.put(
        f"/admin/workspaces/{ws_id}/llm",
        headers={"X-Admin-Key": ADMIN_KEY, "Content-Type": "application/json"},
        json=llm,
    )
    if r.status_code == 200:
        safe_print(f"LLM restored: {llm['provider']} / {llm.get('default_model', '?')}")
    else:
        safe_print(f"Warning: could not restore LLM: {r.text}")


async def save_llm_config(http: httpx.AsyncClient, ws_id: str):
    """Save current LLM config to disk for future restarts."""
    r = await http.get(
        f"/admin/workspaces/{ws_id}/llm",
        headers={"X-Admin-Key": ADMIN_KEY},
    )
    if r.status_code == 200:
        config = load_config()
        llm_data = r.json()
        # We need the API key too — get it from the full config
        r2 = await http.get(f"/admin/workspaces/{ws_id}", headers={"X-Admin-Key": ADMIN_KEY})
        if r2.status_code == 200:
            ws_data = r2.json()
            # The LLM response doesn't include the API key, but it's stored in Redis
            # We can only save what we have
            pass
        config["llm"] = {
            "provider": llm_data.get("provider", "openai"),
            "upstream_url": llm_data.get("upstream_url", "https://api.openai.com"),
            "default_model": llm_data.get("default_model", "gpt-4o"),
            "api_key": config.get("llm", {}).get("api_key", ""),  # Keep existing key
        }
        save_config(config)


# ============================================================
# NATS BRIDGE
# ============================================================
async def run_bridge(local_ws_id: str, local_api_key: str):
    """Connect to NATS and forward requests to local engine. Auto-reconnects on failure."""
    while True:
        try:
            await _bridge_loop(local_ws_id, local_api_key)
        except Exception as e:
            safe_print(f"Bridge connection lost: {e}")
            safe_print("Reconnecting in 3 seconds...")
            await asyncio.sleep(3)


async def _bridge_loop(local_ws_id: str, local_api_key: str):
    """Single bridge connection session."""
    nc = await nats.connect(
        NATS_URL,
        token=NATS_TOKEN,
        connect_timeout=15,
        reconnect_time_wait=2,
        max_reconnect_attempts=5,
        ping_interval=20,
        max_outstanding_pings=5,
    )
    safe_print("Connected to NATS")

    http = httpx.AsyncClient(base_url=ENGINE_URL, timeout=120.0, verify=False)

    async def handle(msg):
        try:
            req = json.loads(msg.data)
            method = req.get("method", "GET")
            path = req.get("path", "/")
            headers = req.get("headers", {})
            body_str = req.get("body", "")

            # Swap auth — remove original API key, inject local one
            h = {}
            for k, v in headers.items():
                if k.lower() not in ("host", "connection", "transfer-encoding", "content-length", "x-api-key"):
                    h[k] = v
            h["X-API-Key"] = local_api_key

            # Swap workspace_id and file_ids in body
            if body_str:
                try:
                    bd = json.loads(body_str)
                    if "workspace_id" in bd:
                        bd["workspace_id"] = local_ws_id
                    if "file_id" in bd and isinstance(bd["file_id"], str):
                        bd["file_id"] = bd["file_id"].replace(f"file:{WORKSPACE_ID}:", f"file:{local_ws_id}:")
                    if "file_ids" in bd and isinstance(bd["file_ids"], list):
                        bd["file_ids"] = [fid.replace(f"file:{WORKSPACE_ID}:", f"file:{local_ws_id}:") for fid in bd["file_ids"]]
                    body_str = json.dumps(bd, ensure_ascii=True)
                except Exception:
                    pass

            safe_print(f">> {method} {path}")

            resp = await http.request(
                method=method,
                url=path,
                headers=h,
                content=body_str.encode("utf-8") if body_str else None,
            )

            # Build response as pure bytes
            resp_body = resp.content.decode("utf-8", errors="replace")
            body_json = json.dumps(resp_body, ensure_ascii=True)
            payload = (
                b'{"status":' + str(resp.status_code).encode()
                + b',"headers":{"Content-Type":"application/json"},"body":'
                + body_json.encode("ascii") + b'}'
            )

            safe_print(f"<< {resp.status_code} {path}")

            if msg.reply:
                await msg.respond(payload)

            # If LLM was just configured, save it
            if path.endswith("/llm") and method == "PUT" and resp.status_code == 200:
                await save_llm_config(http, local_ws_id)

        except Exception as e:
            err_msg = repr(e).encode("ascii", errors="replace").decode("ascii")
            safe_print(f"ERROR: {err_msg}")
            if msg.reply:
                err = json.dumps({"error": err_msg}, ensure_ascii=True)
                p = (
                    b'{"status":502,"headers":{"Content-Type":"application/json"},"body":'
                    + json.dumps(err, ensure_ascii=True).encode("ascii") + b'}'
                )
                await msg.respond(p)

    await nc.subscribe(f"securellm.{WORKSPACE_ID}.request", cb=handle)
    safe_print("Subscribed. Bridge ready!")
    safe_print("")
    safe_print(f"  Engine:    {ENGINE_URL}")
    safe_print(f"  Admin:     {ENGINE_URL}/admin")
    safe_print(f"  NATS:      {NATS_URL}")
    safe_print(f"  Workspace: {local_ws_id}")
    safe_print("")

    # Keep alive — exit loop if disconnected so outer loop reconnects
    while nc.is_connected:
        await asyncio.sleep(1)
    safe_print("NATS disconnected")
    await nc.close()


# ============================================================
# MAIN
# ============================================================
async def main():
    safe_print("=" * 60)
    safe_print("  SecureLLM On-Premise Engine")
    safe_print("=" * 60)
    safe_print("")

    # Start engine
    start_engine()

    # Wait for engine to be ready
    http = httpx.AsyncClient(base_url=ENGINE_URL, timeout=10.0, verify=False)
    safe_print("Waiting for engine...")
    for _ in range(60):
        try:
            r = await http.get("/health")
            if r.status_code == 200:
                safe_print("Engine ready")
                break
        except Exception:
            pass
        await asyncio.sleep(1)
    else:
        safe_print("Engine failed to start!")
        stop_engine()
        return

    # Setup workspace (persistent)
    local_ws_id, local_api_key = await setup_workspace(http)
    await http.aclose()

    # Run bridge
    try:
        await run_bridge(local_ws_id, local_api_key)
    except KeyboardInterrupt:
        pass
    finally:
        stop_engine()
        safe_print("Stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        stop_engine()
        safe_print("Stopped.")
