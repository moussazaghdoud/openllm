"""Customer chat interface — premium privacy-first AI assistant."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["chat"])


@router.get("/chat", response_class=HTMLResponse)
async def chat_page():
    return CHAT_HTML


CHAT_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SecureLLM</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root, [data-theme="dark"] {
  --bg: #0c0d12; --surface: #16181f; --surface2: #1e2029; --surface3: #262833;
  --border: #2a2d3a; --border-light: #353849;
  --text: #eef0f6; --text2: #9299b0; --text3: #6b7190;
  --accent: #7c6ef0; --accent2: #9d93f8; --accent-glow: rgba(124,110,240,.15);
  --green: #34d399; --green-bg: rgba(52,211,153,.08); --green-border: rgba(52,211,153,.2);
  --red: #f87171; --red-bg: rgba(248,113,113,.06); --red-border: rgba(248,113,113,.15);
  --orange: #fbbf24; --orange-bg: rgba(251,191,36,.08);
  --blue: #60a5fa; --blue-bg: rgba(96,165,250,.08);
  --radius: 16px; --radius-sm: 10px; --radius-xs: 6px;
  --shadow: 0 4px 24px rgba(0,0,0,.3);
  --transition: all .25s cubic-bezier(.4,0,.2,1);
}
[data-theme="light"] {
  --bg: #f5f5f7; --surface: #ffffff; --surface2: #f0f0f3; --surface3: #e8e8ed;
  --border: #d8d8e0; --border-light: #c8c8d2;
  --text: #1a1a2e; --text2: #5a5a72; --text3: #8a8aa0;
  --accent: #6c5ce7; --accent2: #7c6ef0; --accent-glow: rgba(124,110,240,.1);
  --green: #059669; --green-bg: rgba(5,150,105,.06); --green-border: rgba(5,150,105,.15);
  --red: #dc2626; --red-bg: rgba(220,38,38,.05); --red-border: rgba(220,38,38,.12);
  --orange: #d97706; --orange-bg: rgba(217,119,6,.06);
  --blue: #2563eb; --blue-bg: rgba(37,99,235,.06);
  --shadow: 0 4px 24px rgba(0,0,0,.08);
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--text); height:100vh; display:flex; flex-direction:column; overflow:hidden; }

/* ── Header ────────────────────────────── */
.header { background:var(--surface); border-bottom:1px solid var(--border); padding:14px 28px; display:flex; align-items:center; justify-content:space-between; flex-shrink:0; backdrop-filter:blur(12px); }
.logo { display:flex; align-items:center; gap:10px; }
.logo-icon { width:32px; height:32px; background:linear-gradient(135deg,var(--accent),#a78bfa); border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:16px; font-weight:700; color:#fff; }
.logo h1 { font-size:17px; font-weight:600; letter-spacing:-.3px; }
.logo h1 span { color:var(--accent2); }
.header-meta { display:flex; align-items:center; gap:10px; }
.pill { padding:4px 12px; border-radius:20px; font-size:11px; font-weight:500; display:flex; align-items:center; gap:5px; }
.pill-green { background:var(--green-bg); color:var(--green); border:1px solid var(--green-border); }
.pill-dot { width:6px; height:6px; border-radius:50%; background:currentColor; }

/* ── Auth ──────────────────────────────── */
.auth-screen { flex:1; display:flex; align-items:center; justify-content:center; background:radial-gradient(ellipse at 50% 30%,rgba(124,110,240,.06),transparent 70%); }
.auth-card { background:var(--surface); border:1px solid var(--border); border-radius:20px; padding:48px; width:460px; max-width:92vw; text-align:center; box-shadow:var(--shadow); }
.auth-card h2 { font-size:26px; font-weight:700; letter-spacing:-.5px; margin-bottom:6px; }
.auth-card .subtitle { color:var(--text2); font-size:14px; line-height:1.6; margin-bottom:32px; }
.auth-card input { width:100%; background:var(--bg); border:1px solid var(--border); color:var(--text); padding:14px 18px; border-radius:var(--radius-sm); font-size:14px; font-family:'SF Mono','Fira Code',monospace; margin-bottom:16px; transition:var(--transition); }
.auth-card input:focus { outline:none; border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-glow); }
.auth-card .btn { width:100%; padding:14px; font-size:15px; font-weight:600; background:linear-gradient(135deg,var(--accent),#a78bfa); color:#fff; border:none; border-radius:var(--radius-sm); cursor:pointer; transition:var(--transition); }
.auth-card .btn:hover { transform:translateY(-1px); box-shadow:0 8px 24px rgba(124,110,240,.3); }
.shield { font-size:48px; margin-bottom:16px; }

/* ── Main Layout ───────────────────────── */
.app { flex:1; display:none; flex-direction:row; overflow:hidden; }

/* ── Sidebar (Zone A) ──────────────────── */
.sidebar { width:320px; background:var(--surface); border-right:1px solid var(--border); display:flex; flex-direction:column; flex-shrink:0; }
.zone-label { padding:16px 20px 8px; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:1px; display:flex; align-items:center; gap:8px; }
.zone-a-label { color:var(--orange); }
.zone-b-label { color:var(--green); }
.zone-divider { height:1px; background:var(--border); margin:8px 20px; }

/* File cards */
.file-list { flex:1; overflow-y:auto; padding:8px 12px; }
.file-card { background:var(--surface2); border:1px solid var(--border); border-radius:var(--radius-sm); padding:14px; margin-bottom:8px; cursor:default; transition:var(--transition); position:relative; overflow:hidden; }
.file-card:hover { border-color:var(--border-light); }
.file-card.zone-a { border-left:3px solid var(--orange); }
.file-card.zone-b { border-left:3px solid var(--green); }
.file-card .fc-header { display:flex; align-items:center; gap:10px; margin-bottom:6px; }
.file-card .fc-icon { font-size:22px; }
.file-card .fc-name { font-size:13px; font-weight:500; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.file-card .fc-size { font-size:11px; color:var(--text3); }
.file-card .fc-status { font-size:11px; display:flex; align-items:center; gap:6px; margin-top:4px; }
.file-card .fc-actions { display:flex; gap:6px; margin-top:10px; }
.fc-btn { padding:6px 12px; border-radius:var(--radius-xs); font-size:11px; font-weight:500; border:1px solid var(--border); background:var(--surface3); color:var(--text2); cursor:pointer; transition:var(--transition); }
.fc-btn:hover { border-color:var(--accent); color:var(--accent2); }
.fc-btn-accent { background:var(--accent-glow); border-color:rgba(124,110,240,.3); color:var(--accent2); }

/* Zone B compact list */
.file-check { display:flex; align-items:center; gap:8px; padding:8px 12px; border-radius:var(--radius-xs); cursor:pointer; transition:var(--transition); border:1px solid transparent; margin-bottom:2px; }
.file-check:hover { background:var(--surface2); }
.file-check.selected { background:var(--green-bg); border-color:var(--green-border); }
.file-check input[type="checkbox"] { accent-color:var(--green); width:15px; height:15px; cursor:pointer; flex-shrink:0; }
.file-check .fc-icon { font-size:16px; flex-shrink:0; }
.file-check .fc-name { font-size:12px; font-weight:500; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.file-check .fc-chars { font-size:10px; color:var(--text3); flex-shrink:0; }
.file-check .fc-del { opacity:0; background:none; border:none; color:var(--text3); cursor:pointer; font-size:14px; padding:0 2px; flex-shrink:0; transition:var(--transition); }
.file-check:hover .fc-del { opacity:1; }
.file-check .fc-del:hover { color:var(--red); }

/* Context bar in chat */
.context-bar { background:var(--surface); border-bottom:1px solid var(--border); padding:10px 32px; display:none; flex-shrink:0; animation:slideDown .2s ease; }
.context-bar.active { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
@keyframes slideDown { from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)} }
.context-bar .cb-label { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.5px; color:var(--green); flex-shrink:0; }
.context-chip { display:inline-flex; align-items:center; gap:5px; background:var(--green-bg); border:1px solid var(--green-border); border-radius:16px; padding:3px 10px; font-size:11px; color:var(--green); }
.context-chip .cc-icon { font-size:12px; }

/* Anonymization progress bar */
.anon-progress { height:3px; background:var(--border); border-radius:2px; margin-top:8px; overflow:hidden; }
.anon-progress .bar { height:100%; border-radius:2px; transition:width .6s ease; }
.bar-wave1 { background:linear-gradient(90deg,var(--blue),var(--accent)); }
.bar-wave2 { background:linear-gradient(90deg,var(--accent),var(--green)); }

/* Preview link */
.fc-preview { font-size:10px; color:var(--green); cursor:pointer; flex-shrink:0; transition:var(--transition); text-decoration:underline; padding:2px 6px; border-radius:4px; background:rgba(16,185,129,.08); position:relative; z-index:2; }
.fc-preview:hover { background:rgba(16,185,129,.18); }

/* Anonymized preview modal */
.anon-modal-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,.6); z-index:9999; align-items:center; justify-content:center; }
.anon-modal-overlay.open { display:flex; }
.anon-modal { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); max-width:680px; width:90%; max-height:80vh; display:flex; flex-direction:column; box-shadow:0 8px 40px rgba(0,0,0,.4); }
.anon-modal-header { padding:16px 20px; border-bottom:1px solid var(--border); display:flex; align-items:center; justify-content:space-between; }
.anon-modal-header h3 { font-size:14px; font-weight:600; color:var(--green); display:flex; align-items:center; gap:8px; }
.anon-modal-close { background:none; border:none; color:var(--text3); font-size:18px; cursor:pointer; padding:4px; }
.anon-modal-close:hover { color:var(--text1); }
.anon-modal-body { padding:20px; overflow-y:auto; font-size:13px; line-height:1.8; color:var(--text2); white-space:pre-wrap; word-break:break-word; font-family:'SF Mono','Fira Code',monospace; }
.anon-modal-body .ph-pii { color:var(--blue); background:rgba(99,145,255,.12); padding:1px 5px; border-radius:3px; font-weight:600; }
.anon-modal-body .ph-ppi { color:var(--orange); background:rgba(255,165,0,.12); padding:1px 5px; border-radius:3px; font-weight:600; }
.anon-modal-hint { padding:12px 20px; border-top:1px solid var(--border); font-size:11px; color:var(--text3); display:flex; align-items:center; gap:6px; }

/* Upload area */
.upload-area { padding:12px; border-top:1px solid var(--border); }
.drop-zone { border:2px dashed var(--border); border-radius:var(--radius-sm); padding:14px 12px; text-align:center; cursor:pointer; transition:var(--transition); }
.drop-zone:hover { border-color:var(--accent); background:var(--accent-glow); }
.drop-zone.dragover { border-color:var(--accent); background:var(--accent-glow); transform:scale(1.01); }
.drop-zone .dz-icon { font-size:20px; display:inline; margin-right:6px; }
.drop-zone .dz-text { font-size:12px; color:var(--text2); display:inline; }
.drop-zone .dz-hint { font-size:10px; color:var(--text3); margin-top:2px; }

/* ── Chat Area (Zone B) ────────────────── */
.chat-area { flex:1; display:flex; flex-direction:column; background:var(--bg); }

/* Messages */
.messages { flex:1; overflow-y:auto; padding:28px 32px; display:flex; flex-direction:column; gap:20px; }
.msg { max-width:72%; animation:msgIn .3s ease; }
@keyframes msgIn { from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)} }
.msg-user { align-self:flex-end; }
.msg-user .bubble { background:linear-gradient(135deg,var(--accent),var(--accent2)); color:#fff; border-radius:var(--radius) var(--radius) 4px var(--radius); padding:14px 18px; font-size:14px; line-height:1.6; box-shadow:0 2px 12px rgba(124,110,240,.2); }
.msg-assistant { align-self:flex-start; }
.msg-assistant .bubble { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius) var(--radius) var(--radius) 4px; padding:14px 18px; font-size:14px; line-height:1.7; }
.msg-assistant .bubble pre { background:var(--bg); border:1px solid var(--border); border-radius:var(--radius-xs); padding:12px; margin:10px 0; overflow-x:auto; font-size:13px; }
.msg-assistant .bubble code { font-family:'SF Mono','Fira Code',monospace; font-size:13px; }
.msg-system { align-self:center; }
.msg-system .bubble { background:var(--surface2); border:1px solid var(--border); color:var(--text2); font-size:12px; padding:10px 20px; border-radius:24px; }

/* Suggested actions */
.suggestions { display:flex; gap:8px; flex-wrap:wrap; padding:0 32px 12px; }
.suggestion { padding:8px 16px; border:1px solid var(--border); border-radius:20px; font-size:12px; color:var(--text2); cursor:pointer; transition:var(--transition); background:var(--surface); }
.suggestion:hover { border-color:var(--accent); color:var(--accent2); background:var(--accent-glow); }

/* Privacy panel */
.privacy-panel { background:var(--surface); border-top:1px solid var(--border); padding:12px 32px; display:none; flex-shrink:0; max-height:160px; overflow-y:auto; }
.privacy-panel.active { display:block; animation:slideUp .2s ease; }
@keyframes slideUp { from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)} }
.privacy-header { display:flex; align-items:center; gap:8px; margin-bottom:8px; font-size:12px; font-weight:500; color:var(--text2); }
.privacy-header .eye { font-size:14px; }
.privacy-content { background:var(--bg); border:1px solid var(--border); border-radius:var(--radius-xs); padding:10px 14px; font-size:12px; font-family:'SF Mono',monospace; line-height:1.6; white-space:pre-wrap; word-break:break-all; }
.ph-ppi { color:var(--orange); font-weight:600; background:var(--orange-bg); padding:1px 4px; border-radius:3px; }
.ph-pii { color:var(--blue); font-weight:600; background:var(--blue-bg); padding:1px 4px; border-radius:3px; }

/* Typing indicator */
.typing { align-self:flex-start; }
.typing .bubble { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius) var(--radius) var(--radius) 4px; padding:16px 22px; display:flex; gap:5px; }
.typing .dot { width:7px; height:7px; background:var(--text3); border-radius:50%; animation:typingBounce .6s infinite alternate; }
.typing .dot:nth-child(2) { animation-delay:.15s; }
.typing .dot:nth-child(3) { animation-delay:.3s; }
@keyframes typingBounce { to{transform:translateY(-5px);opacity:.3} }

/* ── Input Area ────────────────────────── */
.input-area { padding:16px 32px 20px; border-top:1px solid var(--border); flex-shrink:0; background:var(--surface); }
.input-container { display:flex; gap:10px; align-items:flex-end; background:var(--bg); border:1px solid var(--border); border-radius:14px; padding:6px 6px 6px 18px; transition:var(--transition); }
.input-container:focus-within { border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-glow); }
.input-container textarea { flex:1; background:none; border:none; color:var(--text); font-size:14px; font-family:'Inter',sans-serif; resize:none; min-height:24px; max-height:160px; line-height:1.5; padding:8px 0; }
.input-container textarea:focus { outline:none; }
.input-container textarea::placeholder { color:var(--text3); }
.send-btn { width:40px; height:40px; border-radius:10px; background:linear-gradient(135deg,var(--accent),#a78bfa); color:#fff; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:16px; transition:var(--transition); flex-shrink:0; }
.send-btn:hover { transform:scale(1.05); box-shadow:0 4px 16px rgba(124,110,240,.3); }
.send-btn:disabled { background:var(--surface3); transform:none; box-shadow:none; cursor:not-allowed; }
.input-footer { display:flex; justify-content:space-between; align-items:center; margin-top:8px; padding:0 4px; }
.toggle { display:flex; align-items:center; gap:6px; font-size:12px; color:var(--text3); cursor:pointer; }
.toggle input { accent-color:var(--accent); }
.toggle:hover { color:var(--text2); }

/* ── Toast ─────────────────────────────── */
.toast { position:fixed; bottom:28px; right:28px; background:var(--surface); border:1px solid var(--border); border-radius:var(--radius-sm); padding:14px 22px; font-size:13px; z-index:200; box-shadow:var(--shadow); animation:toastIn .3s ease; }
.toast.success { border-color:var(--green-border); }
.toast.error { border-color:var(--red-border); }
@keyframes toastIn { from{transform:translateY(16px);opacity:0}to{transform:translateY(0);opacity:1} }

/* ── Scrollbar ─────────────────────────── */
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:var(--border-light); }

/* ── Responsive ────────────────────────── */
@media(max-width:768px) {
  .sidebar { display:none; }
  .messages { padding:16px; }
  .input-area { padding:12px 16px; }
}
</style>
</head>
<body>

<!-- Header -->
<div class="header">
  <div class="logo">
    <div class="logo-icon">S</div>
    <h1><span>Secure</span>LLM</h1>
    <span id="wsName" style="color:var(--text3);font-size:13px;margin-left:8px"></span>
  </div>
  <div class="header-meta">
    <div class="pill pill-green" id="privacyPill" style="display:none"><span class="pill-dot"></span> Privacy Active</div>
    <button onclick="toggleTheme()" id="themeBtn" style="background:none;border:1px solid var(--border);border-radius:8px;width:36px;height:36px;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;transition:var(--transition);color:var(--text2)" title="Toggle light/dark mode">&#127769;</button>
    <a href="/portal" style="color:var(--text3);font-size:12px;text-decoration:none;transition:var(--transition)" onmouseover="this.style.color='var(--accent2)'" onmouseout="this.style.color='var(--text3)'">Portal</a>
  </div>
</div>

<!-- Auth -->
<div class="auth-screen" id="authScreen">
  <div class="auth-card">
    <div class="shield">&#128737;</div>
    <h2>Secure AI Assistant</h2>
    <p class="subtitle">Your data is anonymized before reaching the AI.<br>No personal or business data ever leaves your control.</p>
    <input type="password" id="authKey" value="slm_G_inHOaazg6-dcbHswPudsgS8G1w6FWltDnVqFus_94" placeholder="API Key" />
    <button class="btn" onclick="login()">Start Chatting</button>
  </div>
</div>

<!-- App -->
<div class="app" id="app">

  <!-- Sidebar: Zone A + Zone B files -->
  <div class="sidebar">
    <div class="zone-label zone-a-label">&#128308; Sensitive Data (Local)</div>
    <div class="file-list" id="zoneAFiles"></div>
    <div class="zone-divider"></div>
    <div class="zone-label zone-b-label">&#128994; AI-Protected Data</div>
    <div class="file-list" id="zoneBFiles"></div>
    <div class="upload-area">
      <div class="drop-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
        <span class="dz-icon">&#128206;</span><span class="dz-text">Drop or click to upload</span>
        <div class="dz-hint">PDF, DOCX, PPTX, XLSX, TXT, CSV</div>
      </div>
      <input type="file" id="fileInput" style="display:none" accept=".txt,.md,.csv,.json,.xml,.pdf,.docx,.doc,.pptx,.ppt,.xlsx,.xls,.py,.js,.ts,.sql,.html,.log,.yaml,.yml" multiple onchange="handleFiles(this.files)" />
    </div>
  </div>

  <!-- Chat Area -->
  <div class="chat-area">
    <div class="context-bar" id="contextBar">
      <span class="cb-label">Working with:</span>
      <div id="contextChips"></div>
    </div>
    <div class="messages" id="messages">
      <div class="msg msg-system"><div class="bubble">All messages and documents are anonymized through a 2-wave privacy pipeline before reaching the AI.</div></div>
    </div>
    <div class="suggestions" id="suggestions" style="display:none">
      <div class="suggestion" onclick="sendSuggestion('Summarize the selected documents')">&#128196; Summarize</div>
      <div class="suggestion" onclick="sendSuggestion('Extract key insights and action items')">&#128161; Extract insights</div>
      <div class="suggestion" onclick="sendSuggestion('List all people and organizations mentioned')">&#128101; Find entities</div>
      <div class="suggestion" onclick="translateSelected()">&#127760; Translate</div>
      <div class="suggestion" onclick="sendSuggestion('Compare the selected documents')">&#128260; Compare</div>
    </div>
    <div class="privacy-panel" id="privacyPanel">
      <div class="privacy-header"><span class="eye">&#128065;</span> What AI sees (anonymized)</div>
      <div class="privacy-content" id="privacyContent"></div>
    </div>
    <div class="input-area">
      <div class="input-container">
        <textarea id="chatInput" placeholder="Ask anything — your data stays protected..." rows="1"></textarea>
        <button class="send-btn" id="sendBtn" onclick="send()">&#9654;</button>
      </div>
      <div class="input-footer">
        <span style="font-size:11px;color:var(--text3)">2-wave anonymization active</span>
      </div>
    </div>
  </div>
</div>

<!-- Anonymized preview modal -->
<div class="anon-modal-overlay" id="anonModal" onclick="if(event.target===this)closeAnonModal()">
  <div class="anon-modal">
    <div class="anon-modal-header">
      <h3>&#128737; What AI sees</h3>
      <button class="anon-modal-close" onclick="closeAnonModal()">&times;</button>
    </div>
    <div class="anon-modal-body" id="anonModalBody"></div>
    <div class="anon-modal-hint">&#128274; All highlighted tokens replace your real data. AI never sees the originals.</div>
  </div>
</div>

<script>
const B = window.location.origin;
let apiKey='', wsId='', wsInfo=null, history=[];
let attachedFiles=[]; // {file_id, filename, size, char_count, status:'uploading'|'wave1'|'wave2'|'ready'}

function hdr(){return{'X-API-Key':apiKey,'Content-Type':'application/json'}}
function toast(m,t=''){const e=document.createElement('div');e.className='toast '+t;e.textContent=m;document.body.appendChild(e);setTimeout(()=>e.remove(),3500)}
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML}
function fmtSize(b){if(b<1024)return b+' B';if(b<1048576)return(b/1024).toFixed(1)+' KB';return(b/1048576).toFixed(1)+' MB'}
function fIcon(n){const e=n.split('.').pop().toLowerCase();const m={pdf:'&#128196;',docx:'&#128196;',doc:'&#128196;',pptx:'&#128202;',ppt:'&#128202;',xlsx:'&#128202;',xls:'&#128202;',csv:'&#128202;',txt:'&#128196;',md:'&#128196;',json:'&#128203;',py:'&#128187;',js:'&#128187;'};return m[e]||'&#128196;'}

// ── Auth ──
async function login(){
  apiKey=document.getElementById('authKey').value.trim();
  if(!apiKey)return toast('Enter your API key','error');
  try{
    const r=await fetch(B+'/portal/api/workspace',{headers:hdr()});
    if(!r.ok)return toast('Invalid API key','error');
    wsInfo=await r.json(); wsId=wsInfo.id;
    document.getElementById('authScreen').style.display='none';
    document.getElementById('app').style.display='flex';
    document.getElementById('wsName').textContent=wsInfo.name;
    document.getElementById('privacyPill').style.display='flex';
    document.getElementById('chatInput').focus();
  }catch(e){toast('Connection error','error')}
}
document.getElementById('authKey').addEventListener('keydown',e=>{if(e.key==='Enter')login()});

// ── File Upload with Magic Animation ──
async function handleFiles(fileList){
  for(const file of fileList){
    if(file.size>50*1048576){toast(file.name+' too large (max 50MB)','error');continue}
    const idx=attachedFiles.length;
    attachedFiles.push({filename:file.name, size:file.size, status:'uploading', file_id:null, char_count:0, progress:0});
    renderFiles();

    // Step 1: Uploading
    await sleep(300);
    attachedFiles[idx].status='uploading';
    attachedFiles[idx].progress=20;
    renderFiles();

    // Step 2: Wave 1 — PPI anonymization
    await sleep(500);
    attachedFiles[idx].status='wave1';
    attachedFiles[idx].progress=40;
    renderFiles();

    // Upload (actual network call — wave 1 + wave 2 happen server-side)
    const form=new FormData(); form.append('file',file);
    try{
      // Start progress animation during upload
      const progressInterval=setInterval(()=>{
        if(attachedFiles[idx]&&attachedFiles[idx].progress<85){
          attachedFiles[idx].progress+=3;
          if(attachedFiles[idx].progress>60&&attachedFiles[idx].status==='wave1'){
            attachedFiles[idx].status='wave2';
          }
          renderFiles();
        }
      },200);

      const r=await fetch(B+'/v1/upload',{method:'POST',headers:{'X-API-Key':apiKey},body:form});
      clearInterval(progressInterval);

      if(!r.ok){const err=await r.json();toast('Upload failed: '+(err.detail||'error'),'error');attachedFiles.splice(idx,1);renderFiles();continue}
      const data=await r.json();

      // Step 3: Wave 2 complete
      attachedFiles[idx].status='wave2';
      attachedFiles[idx].progress=90;
      renderFiles();
      await sleep(400);

      // Step 4: Securing complete
      attachedFiles[idx].progress=100;
      renderFiles();
      await sleep(300);

      // Ready — auto-select
      attachedFiles[idx]={...attachedFiles[idx],file_id:data.file_id,char_count:data.char_count,status:'ready',selected:true};
      renderFiles();
      document.getElementById('suggestions').style.display='flex';
      toast('Secured: '+file.name,'success');
    }catch(e){toast('Error: '+e.message,'error');attachedFiles.splice(idx,1);renderFiles()}
  }
  document.getElementById('fileInput').value='';
}

function sleep(ms){return new Promise(r=>setTimeout(r,ms))}

function renderFiles(){
  const za=document.getElementById('zoneAFiles');
  const zb=document.getElementById('zoneBFiles');
  za.innerHTML=''; zb.innerHTML='';

  attachedFiles.forEach((f,i)=>{
    if(f.status==='ready'){
      // Zone B: compact checkbox list
      const row=document.createElement('div');
      row.className='file-check'+(f.selected?' selected':'');
      row.onclick=()=>{toggleSelect(i,!f.selected)};
      row.innerHTML=`
        <input type="checkbox" ${f.selected?'checked':''} onclick="event.stopPropagation()" onchange="toggleSelect(${i},this.checked)"/>
        <div style="flex:1;min-width:0">
          <div style="display:flex;align-items:center;gap:6px">
            <span class="fc-icon">${fIcon(f.filename)}</span>
            <span class="fc-name">${esc(f.filename)}</span>
            <button class="fc-del" onclick="event.stopPropagation();confirmRemove(${i})" title="Remove">&#10005;</button>
          </div>
          <div style="padding-left:22px;margin-top:3px">
            <a class="fc-preview" onclick="event.stopPropagation();viewAnonymized('${f.file_id}')">&#128065; See what AI sees</a>
          </div>
        </div>`;
      zb.appendChild(row);
    } else {
      // Zone A: compact row with inline progress
      const row=document.createElement('div');
      row.className='file-check';
      row.style.borderLeft='3px solid var(--orange)';
      const labels={uploading:'Uploading...',wave1:'Wave 1: Anonymizing personal data...',wave2:'Wave 2: Anonymizing business data...'};
      const colors={uploading:'var(--text3)',wave1:'var(--blue)',wave2:'var(--orange)'};
      const barColors={uploading:'var(--text3)',wave1:'var(--blue)',wave2:'var(--orange)'};
      const pct=f.progress||0;
      row.innerHTML=`
        <div style="flex:1;min-width:0;overflow:hidden">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:2px">
            <span class="fc-icon" style="flex-shrink:0">${fIcon(f.filename)}</span>
            <span class="fc-name" style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px">${esc(f.filename)}</span>
          </div>
          <div style="font-size:10px;color:${colors[f.status]};margin-bottom:4px;padding-left:24px">${labels[f.status]}</div>
          <div class="anon-progress"><div class="bar" style="width:${pct}%;background:${barColors[f.status]}"></div></div>
        </div>`;
      za.appendChild(row);
    }
  });

  updateContextBar();
}

function toggleSelect(i, checked){
  attachedFiles[i].selected=checked;
  renderFiles();
}

async function viewAnonymized(fileId){
  try{
    const r=await fetch(B+'/v1/files/'+encodeURIComponent(fileId),{headers:hdr()});
    if(!r.ok){toast('Could not load preview','error');return}
    const d=await r.json();
    let h=esc(d.anonymized_text)
      .replace(/\[PRODUCT_\d+\]/g,'<span class="ph-ppi">$&</span>')
      .replace(/\[COMPANY_\d+\]/g,'<span class="ph-ppi">$&</span>')
      .replace(/\[PROJECT_\d+\]/g,'<span class="ph-ppi">$&</span>')
      .replace(/&lt;[A-Z_]+_\d+&gt;/g,'<span class="ph-pii">$&</span>');
    document.getElementById('anonModalBody').innerHTML=h;
    document.getElementById('anonModal').classList.add('open');
  }catch(e){toast('Error: '+e.message,'error')}
}
function closeAnonModal(){document.getElementById('anonModal').classList.remove('open')}

function getSelectedFiles(){
  return attachedFiles.filter(f=>f.selected&&f.file_id);
}

function updateContextBar(){
  const selected=getSelectedFiles();
  const bar=document.getElementById('contextBar');
  const chips=document.getElementById('contextChips');

  if(selected.length===0){
    bar.classList.remove('active');
    return;
  }
  bar.classList.add('active');
  chips.innerHTML=selected.map(f=>`<span class="context-chip"><span class="cc-icon">${fIcon(f.filename)}</span>${esc(f.filename)}</span>`).join('');

  // Show suggestions when files selected
  document.getElementById('suggestions').style.display='flex';
}

function confirmRemove(i){
  const f=attachedFiles[i];if(!f)return;
  if(confirm('Remove "'+f.filename+'" ?')){removeFile(i)}
}
function removeFile(i){attachedFiles.splice(i,1);renderFiles();if(getSelectedFiles().length===0)document.getElementById('suggestions').style.display='none'}

// ── Translation ──
async function translateFile(i,lang){
  const f=attachedFiles[i]; if(!f||!f.file_id)return;
  if(!lang){lang=prompt('Translate to which language?','French');if(!lang)return;}
  addMsg('system','Translating '+f.filename+' to '+lang+'...');
  try{
    const r=await fetch(B+'/v1/translate',{method:'POST',headers:hdr(),body:JSON.stringify({file_id:f.file_id,language:lang})});
    const d=await r.json();
    if(!r.ok){addMsg('system','Error: '+(d.detail||'failed'));return}
    addMsg('assistant',`Translation complete: **${d.filename}**\n${d.paragraphs_translated} paragraphs translated.\n\n[Download](${B}${d.download_url})`);
    toast('Translation complete!','success');
  }catch(e){addMsg('system','Error: '+e.message)}
}

function translateSelected(){
  const selected=getSelectedFiles();
  if(selected.length===0){toast('Select files first','error');return}
  const lang=prompt('Translate to which language?','French');
  if(!lang)return;
  selected.forEach(f=>{const i=attachedFiles.indexOf(f);translateFile(i,lang)});
}

// ── Chat ──
function sendSuggestion(text){document.getElementById('chatInput').value=text;send()}

async function send(){
  const input=document.getElementById('chatInput');
  const text=input.value.trim();
  if(!text)return;
  input.value='';autoResize(input);
  addMsg('user',text);
  document.getElementById('sendBtn').disabled=true;

  // Typing indicator
  const typing=document.createElement('div');
  typing.className='msg typing';
  typing.innerHTML='<div class="bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
  document.getElementById('messages').appendChild(typing);
  scrollEnd();

  history.push({role:'user',content:text});
  const file_ids=getSelectedFiles().map(f=>f.file_id);

  try{
    const r=await fetch(B+'/v1/chat/completions',{method:'POST',headers:hdr(),body:JSON.stringify({workspace_id:wsId,messages:history,model:'default',file_ids})});
    typing.remove();document.getElementById('sendBtn').disabled=false;
    if(!r.ok){const err=await r.json();addMsg('system','Error: '+(err.detail||'Something went wrong'));return}
    const data=await r.json();
    const reply=data.choices?.[0]?.message?.content||'(empty response)';
    history.push({role:'assistant',content:reply});
    addMsg('assistant',reply);
  }catch(e){typing.remove();document.getElementById('sendBtn').disabled=false;addMsg('system','Error: '+e.message)}
}

function addMsg(role,text){
  const wrapper=document.createElement('div');
  wrapper.className='msg msg-'+role;
  const bubble=document.createElement('div');
  bubble.className='bubble';

  if(role==='assistant'){
    let h=esc(text);
    h=h.replace(/```(\w*)\n?([\s\S]*?)```/g,'<pre><code>$2</code></pre>');
    h=h.replace(/`([^`]+)`/g,'<code style="background:var(--bg);padding:2px 5px;border-radius:4px">$1</code>');
    h=h.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
    h=h.replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank" style="color:var(--accent2)">$1</a>');
    h=h.replace(/\n/g,'<br>');
    bubble.innerHTML=h;
  } else {
    bubble.textContent=text;
  }
  wrapper.appendChild(bubble);
  document.getElementById('messages').appendChild(wrapper);
  scrollEnd();
}

function scrollEnd(){const m=document.getElementById('messages');m.scrollTop=m.scrollHeight}

// ── Privacy Panel ──
function togglePrivacy(){}
function showPrivacy(text){
  let h=esc(text)
    .replace(/\[PRODUCT_\d+\]/g,'<span class="ph-ppi">$&</span>')
    .replace(/&lt;[A-Z_]+_\d+&gt;/g,'<span class="ph-pii">$&</span>');
  document.getElementById('privacyContent').innerHTML=h;
}

// ── Drag & Drop ──
const dz=document.getElementById('dropZone');
['dragenter','dragover'].forEach(e=>document.body.addEventListener(e,ev=>{ev.preventDefault();ev.stopPropagation();if(apiKey)dz.classList.add('dragover')}));
['dragleave','drop'].forEach(e=>document.body.addEventListener(e,ev=>{ev.preventDefault();ev.stopPropagation();dz.classList.remove('dragover')}));
document.body.addEventListener('drop',e=>{if(e.dataTransfer.files.length&&apiKey)handleFiles(e.dataTransfer.files)});

// ── Auto-resize ──
const ci=document.getElementById('chatInput');
ci.addEventListener('input',function(){autoResize(this)});
ci.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});
function autoResize(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,160)+'px'}

// ── Theme Toggle ──
function toggleTheme(){
  const html=document.documentElement;
  const current=html.getAttribute('data-theme')||'dark';
  const next=current==='dark'?'light':'dark';
  html.setAttribute('data-theme',next);
  document.getElementById('themeBtn').innerHTML=next==='dark'?'&#127769;':'&#9728;';
  localStorage.setItem('securellm-theme',next);
}
// Restore saved theme
(function(){
  const saved=localStorage.getItem('securellm-theme');
  if(saved){
    document.documentElement.setAttribute('data-theme',saved);
    if(saved==='light')document.getElementById('themeBtn').innerHTML='&#9728;';
  }
})();
</script>
</body>
</html>
"""
