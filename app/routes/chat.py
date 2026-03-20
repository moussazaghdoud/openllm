"""Customer chat interface — privacy-safe LLM chat powered by SecureLLM API."""

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
<title>SecureLLM — Secure Chat</title>
<style>
:root {
  --bg: #0f1117; --surface: #1a1d27; --surface2: #232733; --border: #2e3345;
  --text: #e1e4ed; --text2: #8b90a0;
  --accent: #6c5ce7; --accent2: #a29bfe;
  --green: #00b894; --red: #e17055; --orange: #fdcb6e; --blue: #74b9ff;
  --radius: 10px;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background:var(--bg); color:var(--text); height:100vh; display:flex; flex-direction:column; }

/* Header */
.header { background:var(--surface); border-bottom:1px solid var(--border); padding:12px 24px; display:flex; align-items:center; justify-content:space-between; flex-shrink:0; }
.header h1 { font-size:18px; font-weight:600; }
.header h1 span { color:var(--accent2); }
.header-right { display:flex; align-items:center; gap:10px; }
.badge { padding:3px 8px; border-radius:12px; font-size:11px; font-weight:500; }
.badge-green { background:rgba(0,184,148,.15); color:var(--green); }
.badge-orange { background:rgba(253,203,110,.15); color:var(--orange); }

/* Auth */
.auth-screen { flex:1; display:flex; align-items:center; justify-content:center; }
.auth-box { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:40px; width:440px; max-width:95vw; text-align:center; }
.auth-box h2 { font-size:22px; margin-bottom:8px; }
.auth-box p { color:var(--text2); font-size:14px; margin-bottom:24px; }
.auth-box input { width:100%; background:var(--bg); border:1px solid var(--border); color:var(--text); padding:12px 16px; border-radius:8px; font-size:14px; font-family:'SF Mono',monospace; margin-bottom:16px; }
.auth-box input:focus { outline:none; border-color:var(--accent); }
.auth-box .btn { width:100%; padding:12px; font-size:15px; }

/* Chat layout */
.chat-container { flex:1; display:none; flex-direction:column; max-width:900px; width:100%; margin:0 auto; }

/* Messages */
.messages { flex:1; overflow-y:auto; padding:24px; display:flex; flex-direction:column; gap:16px; }
.msg { max-width:80%; padding:12px 16px; border-radius:12px; font-size:14px; line-height:1.6; word-wrap:break-word; }
.msg-user { align-self:flex-end; background:var(--accent); color:#fff; border-bottom-right-radius:4px; }
.msg-assistant { align-self:flex-start; background:var(--surface); border:1px solid var(--border); border-bottom-left-radius:4px; }
.msg-system { align-self:center; background:var(--surface2); border:1px solid var(--border); color:var(--text2); font-size:12px; padding:8px 16px; border-radius:20px; }
.msg-assistant pre { background:var(--bg); border:1px solid var(--border); border-radius:6px; padding:10px; margin:8px 0; overflow-x:auto; font-size:13px; }
.msg-assistant code { font-family:'SF Mono','Fira Code',monospace; font-size:13px; }
.msg-assistant p { margin:4px 0; }
.typing { align-self:flex-start; padding:12px 20px; background:var(--surface); border:1px solid var(--border); border-radius:12px; border-bottom-left-radius:4px; }
.typing span { display:inline-block; width:8px; height:8px; background:var(--text2); border-radius:50%; margin:0 2px; animation:bounce .6s infinite alternate; }
.typing span:nth-child(2) { animation-delay:.2s; }
.typing span:nth-child(3) { animation-delay:.4s; }
@keyframes bounce { to { transform:translateY(-6px); opacity:.4; } }

/* Privacy panel */
.privacy-panel { background:var(--surface2); border-top:1px solid var(--border); padding:8px 24px; font-size:12px; color:var(--text2); display:none; flex-shrink:0; }
.privacy-panel.active { display:block; }
.privacy-panel .label { color:var(--orange); font-weight:600; margin-right:6px; }
.privacy-panel pre { background:var(--bg); border:1px solid var(--border); border-radius:6px; padding:8px 12px; margin:4px 0; font-size:11px; white-space:pre-wrap; word-break:break-all; overflow:hidden; max-height:120px; overflow-y:auto; }
.placeholder-ppi { color:var(--orange); font-weight:600; }
.placeholder-pii { color:var(--blue); font-weight:600; }

/* Input */
.input-area { padding:16px 24px; border-top:1px solid var(--border); flex-shrink:0; }
.input-row { display:flex; gap:10px; align-items:flex-end; }
.input-row textarea { flex:1; background:var(--surface); border:1px solid var(--border); color:var(--text); padding:12px 16px; border-radius:12px; font-size:14px; font-family:inherit; resize:none; min-height:48px; max-height:200px; line-height:1.5; }
.input-row textarea:focus { outline:none; border-color:var(--accent); }
.send-btn { background:var(--accent); color:#fff; border:none; border-radius:12px; width:48px; height:48px; cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:18px; transition:background .15s; flex-shrink:0; }
.send-btn:hover { background:var(--accent2); }
.send-btn:disabled { background:var(--surface2); cursor:not-allowed; }
.input-footer { display:flex; justify-content:space-between; align-items:center; margin-top:8px; font-size:12px; color:var(--text2); }
.toggle { display:flex; align-items:center; gap:6px; cursor:pointer; }
.toggle input { accent-color:var(--accent); }

/* Toast */
.toast { position:fixed; bottom:24px; right:24px; background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:12px 20px; font-size:13px; z-index:200; animation:slideIn .3s; }
.toast.error { border-color:var(--red); }
@keyframes slideIn { from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1} }

/* Scrollbar */
.messages::-webkit-scrollbar { width:6px; }
.messages::-webkit-scrollbar-track { background:transparent; }
.messages::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
</style>
</head>
<body>

<div class="header">
  <div style="display:flex;align-items:center;gap:12px">
    <h1><span>Secure</span>LLM</h1>
    <span id="wsNameBadge" style="display:none;color:var(--text2);font-size:13px"></span>
  </div>
  <div class="header-right">
    <span id="privacyBadge" class="badge badge-green" style="display:none">Privacy ON</span>
    <span id="llmBadge" class="badge" style="display:none"></span>
    <a href="/portal" style="color:var(--text2);font-size:12px;text-decoration:none" id="portalLink" style="display:none">Portal</a>
  </div>
</div>

<!-- Auth screen -->
<div class="auth-screen" id="authScreen">
  <div class="auth-box">
    <h2>Secure Chat</h2>
    <p>All your messages are anonymized before reaching the AI.<br>No personal data ever leaves your network.</p>
    <input type="password" id="authKey" placeholder="Enter your API key (slm_...)" />
    <button class="btn btn-primary" onclick="login()">Start Chatting</button>
  </div>
</div>

<!-- Chat -->
<div class="chat-container" id="chatContainer">
  <div class="messages" id="messages">
    <div class="msg msg-system">All messages are anonymized through the SecureLLM Privacy Gateway before reaching the AI.</div>
  </div>
  <div class="privacy-panel" id="privacyPanel">
    <span class="label">What the AI sees:</span>
    <pre id="privacyContent"></pre>
  </div>
  <div class="input-area">
    <div class="input-row">
      <textarea id="chatInput" placeholder="Type your message..." rows="1"></textarea>
      <button class="send-btn" id="sendBtn" onclick="send()">&#9654;</button>
    </div>
    <div class="input-footer">
      <label class="toggle"><input type="checkbox" id="showPrivacy" onchange="togglePrivacy()"> Show what AI sees (anonymized view)</label>
      <span id="charCount" style="color:var(--text2)"></span>
    </div>
  </div>
</div>

<script>
const B = window.location.origin;
let apiKey = '';
let wsId = '';
let wsInfo = null;
let history = [];

function hdr() { return { 'X-API-Key': apiKey, 'Content-Type': 'application/json' }; }
function toast(m,t='') { const e=document.createElement('div'); e.className='toast '+t; e.textContent=m; document.body.appendChild(e); setTimeout(()=>e.remove(),3000); }
function esc(s) { const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }

// Auth
async function login() {
  apiKey = document.getElementById('authKey').value.trim();
  if (!apiKey) return toast('Enter your API key','error');
  try {
    const r = await fetch(B+'/portal/api/workspace', {headers:hdr()});
    if (!r.ok) return toast('Invalid API key','error');
    wsInfo = await r.json();
    wsId = wsInfo.id;

    document.getElementById('authScreen').style.display = 'none';
    document.getElementById('chatContainer').style.display = 'flex';
    document.getElementById('wsNameBadge').style.display = 'inline';
    document.getElementById('wsNameBadge').textContent = wsInfo.name;
    document.getElementById('privacyBadge').style.display = 'inline';
    document.getElementById('portalLink').style.display = 'inline';

    const llmBadge = document.getElementById('llmBadge');
    if (wsInfo.llm && wsInfo.llm.configured) {
      llmBadge.textContent = wsInfo.llm.provider;
      llmBadge.className = 'badge badge-green';
      llmBadge.style.display = 'inline';
    } else {
      llmBadge.textContent = 'No LLM';
      llmBadge.className = 'badge badge-orange';
      llmBadge.style.display = 'inline';
    }

    document.getElementById('chatInput').focus();
  } catch(e) { toast('Connection error','error'); }
}

document.getElementById('authKey').addEventListener('keydown', e => { if(e.key==='Enter') login(); });

// Chat
async function send() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  autoResize(input);
  addMessage('user', text);

  const sendBtn = document.getElementById('sendBtn');
  sendBtn.disabled = true;

  // Show typing
  const typingEl = document.createElement('div');
  typingEl.className = 'typing';
  typingEl.innerHTML = '<span></span><span></span><span></span>';
  document.getElementById('messages').appendChild(typingEl);
  scrollBottom();

  // Build messages for API
  history.push({role:'user', content:text});

  try {
    // Step 1: Show anonymized version if panel is open
    if (document.getElementById('showPrivacy').checked) {
      const anonR = await fetch(B+'/v1/anonymize', {
        method:'POST', headers:hdr(),
        body: JSON.stringify({text, workspace_id:wsId})
      });
      if (anonR.ok) {
        const anonD = await anonR.json();
        showPrivacyView(anonD.anonymized_text);
      }
    }

    // Step 2: Send to LLM proxy
    const r = await fetch(B+'/v1/chat/completions', {
      method:'POST', headers:hdr(),
      body: JSON.stringify({
        workspace_id: wsId,
        messages: history,
        model: 'default'
      })
    });

    typingEl.remove();
    sendBtn.disabled = false;

    if (!r.ok) {
      const err = await r.json();
      addMessage('system', 'Error: ' + (err.detail || 'Something went wrong'));
      return;
    }

    const data = await r.json();
    const reply = data.choices?.[0]?.message?.content || '(empty response)';
    history.push({role:'assistant', content:reply});
    addMessage('assistant', reply);

  } catch(e) {
    typingEl.remove();
    sendBtn.disabled = false;
    addMessage('system', 'Error: ' + e.message);
  }
}

function addMessage(role, text) {
  const el = document.createElement('div');
  el.className = 'msg msg-' + role;

  if (role === 'assistant') {
    // Basic markdown: bold, code blocks, inline code, line breaks
    let html = esc(text);
    // Code blocks
    html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code style="background:var(--bg);padding:2px 4px;border-radius:3px">$1</code>');
    // Bold
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Line breaks
    html = html.replace(/\n/g, '<br>');
    el.innerHTML = html;
  } else {
    el.textContent = text;
  }

  document.getElementById('messages').appendChild(el);
  scrollBottom();
}

function scrollBottom() {
  const m = document.getElementById('messages');
  m.scrollTop = m.scrollHeight;
}

// Privacy panel
function togglePrivacy() {
  document.getElementById('privacyPanel').classList.toggle('active',
    document.getElementById('showPrivacy').checked);
}

function showPrivacyView(text) {
  const el = document.getElementById('privacyContent');
  let html = esc(text)
    .replace(/\[PRODUCT_\d+\]/g, '<span class="placeholder-ppi">$&</span>')
    .replace(/&lt;[A-Z_]+_\d+&gt;/g, '<span class="placeholder-pii">$&</span>');
  el.innerHTML = html;
}

// Auto-resize textarea
const chatInput = document.getElementById('chatInput');
chatInput.addEventListener('input', function() { autoResize(this); });
chatInput.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
});

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 200) + 'px';
}

// New chat
function newChat() {
  history = [];
  document.getElementById('messages').innerHTML = '<div class="msg msg-system">All messages are anonymized through the SecureLLM Privacy Gateway before reaching the AI.</div>';
  document.getElementById('privacyContent').innerHTML = '';
}
</script>
</body>
</html>
"""
