"""Admin dashboard — self-contained HTML UI."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])


@router.get("/", response_class=HTMLResponse)
@router.get("/admin", response_class=HTMLResponse)
async def dashboard():
    return DASHBOARD_HTML


DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SecureLLM — Admin Dashboard</title>
<style>
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --surface2: #232733;
  --border: #2e3345;
  --text: #e1e4ed;
  --text2: #8b90a0;
  --accent: #6c5ce7;
  --accent2: #a29bfe;
  --green: #00b894;
  --red: #e17055;
  --orange: #fdcb6e;
  --blue: #74b9ff;
  --radius: 10px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }

/* Header */
.header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
.header h1 { font-size: 20px; font-weight: 600; }
.header h1 span { color: var(--accent2); }
.header-right { display: flex; align-items: center; gap: 12px; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 500; }
.badge-green { background: rgba(0,184,148,.15); color: var(--green); }
.badge-red { background: rgba(225,112,85,.15); color: var(--red); }
.badge-orange { background: rgba(253,203,110,.15); color: var(--orange); }

/* Auth screen */
.auth-screen { position: fixed; inset: 0; z-index: 500; display: flex; align-items: center; justify-content: center; background: var(--bg); }
.auth-screen::before { content: ''; position: absolute; top: -30%; left: 50%; transform: translateX(-50%); width: 600px; height: 600px; background: radial-gradient(circle, rgba(108,92,231,0.08) 0%, rgba(0,184,148,0.04) 40%, transparent 70%); pointer-events: none; }
.auth-card { position: relative; background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 48px 40px; width: 400px; max-width: 90vw; text-align: center; box-shadow: 0 8px 40px rgba(0,0,0,0.3); }
.auth-card .logo-icon { width: 56px; height: 56px; border-radius: 14px; background: linear-gradient(135deg, var(--accent), var(--green)); display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; font-size: 24px; font-weight: 800; color: #fff; }
.auth-card h2 { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
.auth-card .subtitle { font-size: 13px; color: var(--text2); margin-bottom: 28px; }
.auth-card input { width: 100%; background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 13px 16px; border-radius: 8px; font-size: 14px; margin-bottom: 12px; transition: border-color 0.2s; }
.auth-card input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(108,92,231,0.15); }
.auth-card .btn-login { width: 100%; padding: 13px; border-radius: 8px; font-size: 14px; font-weight: 600; background: linear-gradient(135deg, var(--accent), #5a4bd1); color: #fff; border: none; cursor: pointer; transition: all 0.2s; }
.auth-card .btn-login:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(108,92,231,0.3); }
.auth-card .auth-error { color: var(--red); font-size: 12px; margin-top: 8px; display: none; }

/* Layout */
.container { max-width: 1200px; margin: 0 auto; padding: 24px 32px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }

/* Cards */
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; }
.card h3 { font-size: 13px; color: var(--text2); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; }
.card .value { font-size: 28px; font-weight: 700; }
.card .sub { font-size: 12px; color: var(--text2); margin-top: 4px; }

/* Sections */
.section { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 24px; }
.section-header { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
.section-header h2 { font-size: 16px; font-weight: 600; }
.section-body { padding: 20px; }

/* Table */
table { width: 100%; border-collapse: collapse; }
th { text-align: left; font-size: 12px; color: var(--text2); text-transform: uppercase; letter-spacing: .5px; padding: 8px 12px; border-bottom: 1px solid var(--border); }
td { padding: 12px; border-bottom: 1px solid var(--border); font-size: 14px; vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(108,92,231,.05); }

/* Buttons */
.btn { padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 500; border: none; cursor: pointer; transition: all .15s; }
.btn-primary { background: var(--accent); color: #fff; }
.btn-primary:hover { background: var(--accent2); }
.btn-danger { background: transparent; color: var(--red); border: 1px solid var(--red); }
.btn-danger:hover { background: rgba(225,112,85,.1); }
.btn-sm { padding: 5px 10px; font-size: 12px; }
.btn-ghost { background: transparent; color: var(--accent2); border: 1px solid var(--border); }
.btn-ghost:hover { border-color: var(--accent2); }

/* Forms */
.form-row { display: flex; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.form-group { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 180px; }
.form-group label { font-size: 12px; color: var(--text2); }
.form-group input, .form-group select, .form-group textarea { background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; border-radius: 6px; font-size: 13px; font-family: inherit; }
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: var(--accent); }
textarea { resize: vertical; min-height: 60px; }

/* Modal */
.modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.6); z-index: 100; align-items: center; justify-content: center; }
.modal-overlay.active { display: flex; }
.modal { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); width: 560px; max-width: 95vw; max-height: 90vh; overflow-y: auto; }
.modal-header { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
.modal-header h2 { font-size: 16px; }
.modal-close { background: none; border: none; color: var(--text2); font-size: 20px; cursor: pointer; }
.modal-body { padding: 20px; }
.modal-footer { padding: 12px 20px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 8px; }

/* Test area */
.test-area { display: flex; gap: 12px; }
.test-area textarea { flex: 1; min-height: 100px; }
.test-result { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; font-size: 13px; white-space: pre-wrap; word-break: break-all; margin-top: 8px; min-height: 60px; }
.test-result .placeholder-ppi { color: var(--orange); font-weight: 600; }
.test-result .placeholder-pii { color: var(--blue); font-weight: 600; }

/* Toast */
.toast { position: fixed; bottom: 24px; right: 24px; background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 12px 20px; font-size: 13px; z-index: 200; animation: slideIn .3s; }
.toast.error { border-color: var(--red); }
.toast.success { border-color: var(--green); }
@keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

/* Copy */
.copy-btn { background: none; border: none; color: var(--text2); cursor: pointer; font-size: 14px; padding: 2px 6px; }
.copy-btn:hover { color: var(--accent2); }
.mono { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; background: var(--bg); padding: 2px 6px; border-radius: 4px; }

/* Empty state */
.empty { text-align: center; padding: 40px; color: var(--text2); }
.empty p { margin-top: 8px; font-size: 14px; }
</style>
</head>
<body>

<div class="header">
  <h1><span>Secure</span>LLM</h1>
  <div class="header-right">
    <span id="healthBadge" class="badge badge-orange">checking...</span>
    <span id="versionBadge" class="badge" style="background:var(--surface2);color:var(--text2)">v0.1.0</span>
  </div>
</div>

<div class="auth-screen" id="authScreen">
  <div class="auth-card">
    <div class="logo-icon">S</div>
    <h2>Admin Dashboard</h2>
    <p class="subtitle">Sign in to manage workspaces and users</p>
    <input type="email" id="adminEmail" placeholder="Email" autocomplete="email" />
    <input type="password" id="adminPassword" placeholder="Password" autocomplete="current-password" />
    <button class="btn-login" onclick="checkAuth()">Sign In</button>
    <p class="auth-error" id="authError"></p>
  </div>
</div>

<div class="container" id="mainContent" style="display:none">

  <!-- Stats -->
  <div class="grid" id="statsGrid">
    <div class="card"><h3>Workspaces</h3><div class="value" id="statWorkspaces">-</div></div>
    <div class="card"><h3>Presidio</h3><div class="value" id="statPresidio" style="font-size:16px">-</div></div>
    <div class="card"><h3>Redis</h3><div class="value" id="statRedis" style="font-size:16px">-</div></div>
    <div class="card"><h3>Status</h3><div class="value" id="statStatus" style="font-size:16px">-</div></div>
  </div>

  <!-- Workspaces -->
  <div class="section">
    <div class="section-header">
      <h2>Workspaces</h2>
      <button class="btn btn-primary btn-sm" onclick="openCreateModal()">+ New Workspace</button>
    </div>
    <div class="section-body" id="workspacesBody">
      <div class="empty"><p>Loading...</p></div>
    </div>
  </div>

  <!-- Users -->
  <div class="section">
    <div class="section-header">
      <h2>Users</h2>
      <button class="btn btn-primary btn-sm" onclick="createUser()">+ New User</button>
    </div>
    <div class="section-body" id="usersGrid">
      <div class="empty"><p>Loading...</p></div>
    </div>
  </div>

  <!-- Live Test -->
  <div class="section">
    <div class="section-header"><h2>Live Anonymization Test</h2></div>
    <div class="section-body">
      <div class="form-row">
        <div class="form-group">
          <label>Workspace</label>
          <select id="testWsSelect"><option value="">Select workspace...</option></select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Input Text</label>
          <textarea id="testInput" placeholder="John Smith from ALE deployed OmniSwitch 6900. Email: john@acme.com"></textarea>
        </div>
      </div>
      <button class="btn btn-primary" onclick="runTest()">Anonymize</button>
      <div id="testOutput" class="test-result" style="display:none"></div>
    </div>
  </div>
</div>

<!-- Create Workspace Modal -->
<div class="modal-overlay" id="createModal">
  <div class="modal">
    <div class="modal-header">
      <h2>Create Workspace</h2>
      <button class="modal-close" onclick="closeModal('createModal')">&times;</button>
    </div>
    <div class="modal-body">
      <div class="form-row">
        <div class="form-group"><label>Name</label><input id="cwName" placeholder="my-workspace" /></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Custom PPI Terms (one per line)</label><textarea id="cwPPI" placeholder="SecretProduct X&#10;InternalTool Y"></textarea></div>
      </div>
      <h3 style="margin:16px 0 8px;font-size:13px;color:var(--text2)">LLM Configuration (optional)</h3>
      <div class="form-row">
        <div class="form-group">
          <label>Provider</label>
          <select id="cwProvider">
            <option value="">None</option>
            <option value="anthropic">Anthropic (Claude)</option>
            <option value="openai">OpenAI</option>
            <option value="openclaw">OpenClaw</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        <div class="form-group"><label>Default Model</label><input id="cwModel" placeholder="claude-sonnet-4-20250514" /></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Upstream URL</label><input id="cwUrl" placeholder="https://api.anthropic.com" /></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>API Key</label><input type="password" id="cwApiKey" placeholder="sk-ant-..." /></div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-ghost" onclick="closeModal('createModal')">Cancel</button>
      <button class="btn btn-primary" onclick="createWorkspace()">Create</button>
    </div>
  </div>
</div>

<!-- LLM Config Modal -->
<div class="modal-overlay" id="llmModal">
  <div class="modal">
    <div class="modal-header">
      <h2>Configure LLM</h2>
      <button class="modal-close" onclick="closeModal('llmModal')">&times;</button>
    </div>
    <div class="modal-body">
      <input type="hidden" id="llmWsId" />
      <div class="form-row">
        <div class="form-group">
          <label>Provider</label>
          <select id="llmProvider">
            <option value="anthropic">Anthropic (Claude)</option>
            <option value="openai">OpenAI</option>
            <option value="openclaw">OpenClaw</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        <div class="form-group"><label>Default Model</label><input id="llmModel" /></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Upstream URL</label><input id="llmUrl" /></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>API Key</label><input type="password" id="llmApiKey" placeholder="Enter new key or leave blank to keep current" /></div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-danger btn-sm" onclick="deleteLLM()" style="margin-right:auto">Remove LLM</button>
      <button class="btn btn-ghost" onclick="closeModal('llmModal')">Cancel</button>
      <button class="btn btn-primary" onclick="saveLLM()">Save</button>
    </div>
  </div>
</div>

<!-- API Key Created Modal -->
<div class="modal-overlay" id="keyModal">
  <div class="modal">
    <div class="modal-header">
      <h2>Workspace Created</h2>
      <button class="modal-close" onclick="closeModal('keyModal')">&times;</button>
    </div>
    <div class="modal-body">
      <p style="margin-bottom:12px;color:var(--text2);font-size:14px">Save this API key — it won't be shown again.</p>
      <div style="display:flex;align-items:center;gap:8px;background:var(--bg);padding:12px;border-radius:6px;border:1px solid var(--border)">
        <code id="createdKey" class="mono" style="flex:1;word-break:break-all"></code>
        <button class="copy-btn" onclick="copyKey()" title="Copy">&#x1f4cb;</button>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-primary" onclick="closeModal('keyModal')">Done</button>
    </div>
  </div>
</div>

<script>
const BASE = window.location.origin;
let workspaces = [];
let wsApiKeys = {};  // ws_id -> api_key (only for current session)

function getHeaders() { return { 'Content-Type': 'application/json' }; }
// Patch fetch to always include credentials
const _origFetch = window.fetch;
window.fetch = function(url, opts = {}) { opts.credentials = opts.credentials || 'same-origin'; return _origFetch(url, opts); };

function toast(msg, type = '') {
  const t = document.createElement('div');
  t.className = 'toast ' + type;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

// Auth
async function checkAuth() {
  const email = document.getElementById('adminEmail').value.trim();
  const password = document.getElementById('adminPassword').value;
  const errEl = document.getElementById('authError');
  errEl.textContent = '';
  if (!email || !password) { errEl.textContent = 'Enter email and password'; errEl.style.display = 'block'; return; }
  try {
    const lr = await fetch(BASE + '/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }), credentials: 'same-origin' });
    if (!lr.ok) { const d = await lr.json().catch(() => ({})); errEl.textContent = d.detail || 'Invalid credentials'; errEl.style.display = 'block'; return; }
    const data = await lr.json();
    if (data.user.role !== 'admin') { errEl.textContent = 'Admin access required'; errEl.style.display = 'block'; return; }
    enterDashboard(data.user.email);
  } catch(e) { errEl.textContent = 'Connection failed: ' + e.message; errEl.style.display = 'block'; }
}
async function enterDashboard(email) {
  document.getElementById('authScreen').style.display = 'none';
  document.getElementById('mainContent').style.display = 'block';
  const h = await (await fetch(BASE + '/health')).json();
  updateHealth(h);
  await loadWorkspaces();
  await loadUsers();
  if (email) toast('Signed in as ' + email, 'success');
}
// Auto-login if session exists
(async()=>{try{const r=await fetch(BASE+'/auth/me',{credentials:'same-origin'});if(r.ok){const d=await r.json();if(d.role==='admin') enterDashboard()}}catch(e){}})();

// Health
async function updateHealth(h) {
  document.getElementById('statPresidio').textContent = h.presidio;
  document.getElementById('statRedis').textContent = h.redis;
  document.getElementById('statStatus').textContent = h.status;
  document.getElementById('versionBadge').textContent = h.version;
  const badge = document.getElementById('healthBadge');
  badge.textContent = h.status;
  badge.className = 'badge ' + (h.status === 'ok' ? 'badge-green' : 'badge-red');
}

// Workspaces
async function loadWorkspaces() {
  // We need to scan for workspaces. The API doesn't have a list endpoint yet,
  // so we'll track them client-side from creation. Let's add a list endpoint.
  // For now, try fetching known workspaces or show empty state.
  try {
    const r = await fetch(BASE + '/admin/workspaces', { headers: getHeaders() });
    if (r.ok) {
      workspaces = await r.json();
    } else {
      workspaces = [];
    }
  } catch { workspaces = []; }
  renderWorkspaces();
}

function renderWorkspaces() {
  const body = document.getElementById('workspacesBody');
  const sel = document.getElementById('testWsSelect');
  document.getElementById('statWorkspaces').textContent = workspaces.length;

  sel.innerHTML = '<option value="">Select workspace...</option>';
  workspaces.forEach(ws => {
    sel.innerHTML += `<option value="${ws.id}">${ws.name}</option>`;
  });

  if (workspaces.length === 0) {
    body.innerHTML = '<div class="empty"><p>No workspaces yet. Create one to get started.</p></div>';
    return;
  }

  let html = '<table><thead><tr><th>Name</th><th>ID</th><th>PPI Terms</th><th>LLM</th><th>Max File</th><th style="width:180px">Actions</th></tr></thead><tbody>';
  workspaces.forEach(ws => {
    const llmBadge = ws.llm && ws.llm.configured
      ? `<span class="badge badge-green">${ws.llm.provider}</span>`
      : '<span class="badge badge-orange">not configured</span>';
    const maxFile = ws.max_file_size_mb || 50;
    html += `<tr>
      <td><strong>${esc(ws.name)}</strong></td>
      <td><span class="mono">${ws.id}</span></td>
      <td>${ws.ppi_term_count}</td>
      <td>${llmBadge}</td>
      <td><input type="number" value="${maxFile}" min="1" max="500" style="width:60px;background:var(--bg);border:1px solid var(--border);color:var(--text);border-radius:4px;padding:4px;text-align:center" onchange="updateMaxFile('${ws.id}',this.value)"> MB</td>
      <td>
        <button class="btn btn-ghost btn-sm" onclick="openLLMModal('${ws.id}')">LLM</button>
        <button class="btn btn-danger btn-sm" onclick="deleteWorkspace('${ws.id}')">Delete</button>
      </td>
    </tr>`;
  });
  html += '</tbody></table>';
  body.innerHTML = html;
}

function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

// Create workspace
function openCreateModal() {
  ['cwName','cwPPI','cwProvider','cwModel','cwUrl','cwApiKey'].forEach(id => {
    const el = document.getElementById(id);
    if (el.tagName === 'SELECT') el.selectedIndex = 0; else el.value = '';
  });
  openModal('createModal');
}

async function createWorkspace() {
  const name = document.getElementById('cwName').value.trim();
  if (!name) return toast('Name is required', 'error');

  const ppiRaw = document.getElementById('cwPPI').value.trim();
  const ppi_terms = ppiRaw ? ppiRaw.split('\n').map(s => s.trim()).filter(Boolean) : [];

  const provider = document.getElementById('cwProvider').value;
  let body = { name, ppi_terms };

  if (provider) {
    const url = document.getElementById('cwUrl').value.trim();
    const key = document.getElementById('cwApiKey').value.trim();
    if (!url || !key) return toast('LLM URL and API key required', 'error');
    body.llm = {
      provider,
      upstream_url: url,
      api_key: key,
      default_model: document.getElementById('cwModel').value.trim()
    };
  }

  try {
    const r = await fetch(BASE + '/admin/workspaces', {
      method: 'POST', headers: getHeaders(), body: JSON.stringify(body)
    });
    const data = await r.json();
    if (!r.ok) return toast(data.detail || 'Error', 'error');

    closeModal('createModal');

    // Store API key for test area
    if (data.api_key) {
      wsApiKeys[data.id] = data.api_key;
      document.getElementById('createdKey').textContent = data.api_key;
      openModal('keyModal');
    }

    await loadWorkspaces();
    toast('Workspace created', 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

function copyKey() {
  navigator.clipboard.writeText(document.getElementById('createdKey').textContent);
  toast('Copied!', 'success');
}

// Delete workspace
async function updateMaxFile(id, val) {
  const mb = parseInt(val);
  if (isNaN(mb) || mb < 1) return toast('Invalid size', 'error');
  const r = await fetch(`${B}/admin/workspaces/${id}`, {method:'PATCH', headers:getHeaders(), body:JSON.stringify({max_file_size_mb:mb})});
  if (r.ok) toast(`Max file size: ${mb} MB`, 'success');
  else toast('Update failed', 'error');
}

async function deleteWorkspace(id) {
  if (!confirm('Delete this workspace? This cannot be undone.')) return;
  try {
    const r = await fetch(BASE + '/admin/workspaces/' + id, { method: 'DELETE', headers: getHeaders() });
    if (!r.ok) { const d = await r.json(); return toast(d.detail || 'Error', 'error'); }
    delete wsApiKeys[id];
    await loadWorkspaces();
    toast('Workspace deleted', 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

// LLM Config
async function openLLMModal(wsId) {
  document.getElementById('llmWsId').value = wsId;
  try {
    const r = await fetch(BASE + '/admin/workspaces/' + wsId + '/llm', { headers: getHeaders() });
    if (r.ok) {
      const cfg = await r.json();
      document.getElementById('llmProvider').value = cfg.provider;
      document.getElementById('llmModel').value = cfg.default_model || '';
      document.getElementById('llmUrl').value = cfg.upstream_url;
      document.getElementById('llmApiKey').value = '';
    } else {
      document.getElementById('llmProvider').value = 'anthropic';
      document.getElementById('llmModel').value = '';
      document.getElementById('llmUrl').value = '';
      document.getElementById('llmApiKey').value = '';
    }
  } catch {}
  openModal('llmModal');
}

async function saveLLM() {
  const wsId = document.getElementById('llmWsId').value;
  const key = document.getElementById('llmApiKey').value.trim();
  if (!key) return toast('API key is required', 'error');
  const body = {
    provider: document.getElementById('llmProvider').value,
    upstream_url: document.getElementById('llmUrl').value.trim(),
    api_key: key,
    default_model: document.getElementById('llmModel').value.trim()
  };
  if (!body.upstream_url) return toast('URL is required', 'error');
  try {
    const r = await fetch(BASE + '/admin/workspaces/' + wsId + '/llm', {
      method: 'PUT', headers: getHeaders(), body: JSON.stringify(body)
    });
    if (!r.ok) { const d = await r.json(); return toast(d.detail || 'Error', 'error'); }
    closeModal('llmModal');
    await loadWorkspaces();
    toast('LLM config saved', 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

async function deleteLLM() {
  const wsId = document.getElementById('llmWsId').value;
  if (!confirm('Remove LLM configuration?')) return;
  try {
    await fetch(BASE + '/admin/workspaces/' + wsId + '/llm', { method: 'DELETE', headers: getHeaders() });
    closeModal('llmModal');
    await loadWorkspaces();
    toast('LLM config removed', 'success');
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

// Live test
async function runTest() {
  const wsId = document.getElementById('testWsSelect').value;
  if (!wsId) return toast('Select a workspace', 'error');
  const text = document.getElementById('testInput').value.trim();
  if (!text) return toast('Enter text to anonymize', 'error');

  const apiKey = wsApiKeys[wsId];
  if (!apiKey) return toast('No API key for this workspace. Create a new workspace or re-enter the key.', 'error');

  const out = document.getElementById('testOutput');
  out.style.display = 'block';
  out.innerHTML = '<span style="color:var(--text2)">Anonymizing...</span>';

  try {
    const r = await fetch(BASE + '/v1/anonymize', {
      method: 'POST',
      headers: { 'X-API-Key': apiKey, 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, workspace_id: wsId })
    });
    const data = await r.json();
    if (!r.ok) return out.innerHTML = '<span style="color:var(--red)">' + esc(data.detail || 'Error') + '</span>';

    // Highlight placeholders
    let highlighted = esc(data.anonymized_text)
      .replace(/\[PRODUCT_\d+\]/g, '<span class="placeholder-ppi">$&</span>')
      .replace(/&lt;[A-Z_]+_\d+&gt;/g, '<span class="placeholder-pii">$&</span>');

    out.innerHTML = `<div style="margin-bottom:8px"><strong>Anonymized:</strong></div>${highlighted}
<div style="margin-top:12px;font-size:12px;color:var(--text2)">Mapping ID: <span class="mono">${esc(data.mapping_id)}</span></div>`;
  } catch(e) { out.innerHTML = '<span style="color:var(--red)">Error: ' + esc(e.message) + '</span>'; }
}

// Provider hint auto-fill
document.getElementById('cwProvider').addEventListener('change', function() {
  const hints = {
    anthropic: { url: 'https://api.anthropic.com', model: 'claude-sonnet-4-20250514' },
    openai: { url: 'https://api.openai.com', model: 'gpt-4o' },
    openclaw: { url: 'https://openclaw-production-6a99.up.railway.app', model: 'openclaw:main' },
  };
  const h = hints[this.value];
  if (h) {
    document.getElementById('cwUrl').value = h.url;
    document.getElementById('cwModel').value = h.model;
  }
});

document.getElementById('llmProvider').addEventListener('change', function() {
  const hints = {
    anthropic: { url: 'https://api.anthropic.com', model: 'claude-sonnet-4-20250514' },
    openai: { url: 'https://api.openai.com', model: 'gpt-4o' },
    openclaw: { url: 'https://openclaw-production-6a99.up.railway.app', model: 'openclaw:main' },
  };
  const h = hints[this.value];
  if (h) {
    document.getElementById('llmUrl').value = h.url;
    document.getElementById('llmModel').value = h.model;
  }
});

// ── User Management ──
let users = [];
async function loadUsers() {
  try {
    const r = await fetch(BASE + '/admin/users', { headers: getHeaders() });
    if (!r.ok) return;
    users = await r.json();
    renderUsers();
  } catch(e) {}
}

function renderUsers() {
  let el = document.getElementById('usersGrid');
  if (!el) return;
  el.innerHTML = users.map(u => `
    <div class="card" style="padding:16px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <strong>${u.email}</strong>
          <span class="badge ${u.role==='admin'?'badge-purple':'badge-green'}" style="margin-left:8px">${u.role}</span>
        </div>
        <button class="btn btn-sm" style="color:#EF4444;border-color:#EF4444" onclick="deleteUser('${u.id}')">Delete</button>
      </div>
      ${u.workspace_id ? '<div style="font-size:11px;color:var(--text3);margin-top:4px">Workspace: '+u.workspace_id+'</div>' : ''}
    </div>
  `).join('');
}

async function createUser() {
  const email = prompt('Email:');
  if (!email) return;
  const password = prompt('Password:');
  if (!password) return;
  const role = prompt('Role (admin or user):', 'user');
  let workspace_id = null;
  if (role === 'user') {
    workspace_id = prompt('Workspace ID (from list above):');
  }
  try {
    const r = await fetch(BASE + '/admin/users', {
      method: 'POST', headers: getHeaders(),
      body: JSON.stringify({ email, password, role, workspace_id })
    });
    if (!r.ok) { const d = await r.json(); toast(d.detail || 'Error', 'error'); return; }
    toast('User created', 'success');
    await loadUsers();
  } catch(e) { toast('Error: ' + e.message, 'error'); }
}

async function deleteUser(id) {
  if (!confirm('Delete this user?')) return;
  await fetch(BASE + '/admin/users/' + id, { method: 'DELETE', headers: getHeaders() });
  toast('User deleted', 'success');
  await loadUsers();
}

// Init: check health on load
fetch(BASE + '/health').then(r => r.json()).then(updateHealth).catch(() => {
  document.getElementById('healthBadge').textContent = 'offline';
  document.getElementById('healthBadge').className = 'badge badge-red';
});

// Enter key on password input
document.getElementById('adminPassword').addEventListener('keydown', e => { if (e.key === 'Enter') checkAuth(); });
</script>
</body>
</html>
"""
