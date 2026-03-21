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
.header { background:var(--surface); border-bottom:1px solid var(--border); padding:12px 24px; display:flex; align-items:center; justify-content:space-between; flex-shrink:0; }
.header h1 { font-size:18px; font-weight:600; }
.header h1 span { color:var(--accent2); }
.header-right { display:flex; align-items:center; gap:10px; }
.badge { padding:3px 8px; border-radius:12px; font-size:11px; font-weight:500; }
.badge-green { background:rgba(0,184,148,.15); color:var(--green); }
.badge-orange { background:rgba(253,203,110,.15); color:var(--orange); }
.auth-screen { flex:1; display:flex; align-items:center; justify-content:center; }
.auth-box { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:40px; width:440px; max-width:95vw; text-align:center; }
.auth-box h2 { font-size:22px; margin-bottom:8px; }
.auth-box p { color:var(--text2); font-size:14px; margin-bottom:24px; }
.auth-box input { width:100%; background:var(--bg); border:1px solid var(--border); color:var(--text); padding:12px 16px; border-radius:8px; font-size:14px; font-family:'SF Mono',monospace; margin-bottom:16px; }
.auth-box input:focus { outline:none; border-color:var(--accent); }
.auth-box .btn { width:100%; padding:12px; font-size:15px; }
.btn { padding:8px 16px; border-radius:6px; font-size:13px; font-weight:500; border:none; cursor:pointer; }
.btn-primary { background:var(--accent); color:#fff; }
.btn-primary:hover { background:var(--accent2); }
.chat-container { flex:1; display:none; flex-direction:column; max-width:900px; width:100%; margin:0 auto; }
.messages { flex:1; overflow-y:auto; padding:24px; display:flex; flex-direction:column; gap:16px; }
.msg { max-width:80%; padding:12px 16px; border-radius:12px; font-size:14px; line-height:1.6; word-wrap:break-word; }
.msg-user { align-self:flex-end; background:var(--accent); color:#fff; border-bottom-right-radius:4px; }
.msg-assistant { align-self:flex-start; background:var(--surface); border:1px solid var(--border); border-bottom-left-radius:4px; }
.msg-system { align-self:center; background:var(--surface2); border:1px solid var(--border); color:var(--text2); font-size:12px; padding:8px 16px; border-radius:20px; }
.msg-assistant pre { background:var(--bg); border:1px solid var(--border); border-radius:6px; padding:10px; margin:8px 0; overflow-x:auto; font-size:13px; }
.msg-assistant code { font-family:'SF Mono','Fira Code',monospace; font-size:13px; }
.typing { align-self:flex-start; padding:12px 20px; background:var(--surface); border:1px solid var(--border); border-radius:12px; border-bottom-left-radius:4px; }
.typing span { display:inline-block; width:8px; height:8px; background:var(--text2); border-radius:50%; margin:0 2px; animation:bounce .6s infinite alternate; }
.typing span:nth-child(2) { animation-delay:.2s; }
.typing span:nth-child(3) { animation-delay:.4s; }
@keyframes bounce { to { transform:translateY(-6px); opacity:.4; } }
.privacy-panel { background:var(--surface2); border-top:1px solid var(--border); padding:8px 24px; font-size:12px; color:var(--text2); display:none; flex-shrink:0; }
.privacy-panel.active { display:block; }
.privacy-panel .label { color:var(--orange); font-weight:600; margin-right:6px; }
.privacy-panel pre { background:var(--bg); border:1px solid var(--border); border-radius:6px; padding:8px 12px; margin:4px 0; font-size:11px; white-space:pre-wrap; word-break:break-all; max-height:120px; overflow-y:auto; }
.placeholder-ppi { color:var(--orange); font-weight:600; }
.placeholder-pii { color:var(--blue); font-weight:600; }

/* File attachment */
.file-bar { background:var(--surface2); border-top:1px solid var(--border); padding:8px 24px; display:none; flex-shrink:0; }
.file-bar.active { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.file-chip { display:inline-flex; align-items:center; gap:6px; background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:6px 12px; font-size:13px; }
.file-chip .file-icon { font-size:16px; }
.file-chip .file-name { max-width:200px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.file-chip .file-size { color:var(--text2); font-size:11px; }
.file-chip .file-remove { background:none; border:none; color:var(--text2); cursor:pointer; font-size:14px; padding:0 2px; }
.file-chip .file-remove:hover { color:var(--red); }
.file-chip.uploading { opacity:.6; }
.file-chip.uploading .file-name::after { content:'  uploading...'; color:var(--orange); }

.input-area { padding:16px 24px; border-top:1px solid var(--border); flex-shrink:0; }
.input-row { display:flex; gap:10px; align-items:flex-end; }
.input-row textarea { flex:1; background:var(--surface); border:1px solid var(--border); color:var(--text); padding:12px 16px; border-radius:12px; font-size:14px; font-family:inherit; resize:none; min-height:48px; max-height:200px; line-height:1.5; }
.input-row textarea:focus { outline:none; border-color:var(--accent); }
.attach-btn { background:var(--surface); color:var(--text2); border:1px solid var(--border); border-radius:12px; width:48px; height:48px; cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:20px; transition:all .15s; flex-shrink:0; }
.attach-btn:hover { border-color:var(--accent); color:var(--accent2); }
.send-btn { background:var(--accent); color:#fff; border:none; border-radius:12px; width:48px; height:48px; cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:18px; transition:background .15s; flex-shrink:0; }
.send-btn:hover { background:var(--accent2); }
.send-btn:disabled { background:var(--surface2); cursor:not-allowed; }
.input-footer { display:flex; justify-content:space-between; align-items:center; margin-top:8px; font-size:12px; color:var(--text2); }
.toggle { display:flex; align-items:center; gap:6px; cursor:pointer; }
.toggle input { accent-color:var(--accent); }
.toast { position:fixed; bottom:24px; right:24px; background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:12px 20px; font-size:13px; z-index:200; animation:slideIn .3s; }
.toast.error { border-color:var(--red); } .toast.success { border-color:var(--green); }
@keyframes slideIn { from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1} }
.messages::-webkit-scrollbar { width:6px; }
.messages::-webkit-scrollbar-track { background:transparent; }
.messages::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }

/* File message */
.msg-file { display:flex; align-items:center; gap:8px; background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:10px 14px; margin-bottom:4px; font-size:13px; max-width:80%; align-self:flex-end; }
.msg-file .fi { font-size:24px; }
.msg-file .fd { display:flex; flex-direction:column; }
.msg-file .fn { font-weight:500; }
.msg-file .fs { color:var(--text2); font-size:11px; }
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
    <a href="/portal" style="color:var(--text2);font-size:12px;text-decoration:none" id="portalLink">Portal</a>
  </div>
</div>

<div class="auth-screen" id="authScreen">
  <div class="auth-box">
    <h2>Secure Chat</h2>
    <p>All your messages are anonymized before reaching the AI.<br>Attach documents for privacy-safe analysis.</p>
    <input type="password" id="authKey" placeholder="Enter your API key (slm_...)" />
    <button class="btn btn-primary" onclick="login()">Start Chatting</button>
  </div>
</div>

<div class="chat-container" id="chatContainer">
  <div class="messages" id="messages">
    <div class="msg msg-system">All messages and documents are anonymized before reaching the AI. Attach files with the clip button.</div>
  </div>
  <div class="privacy-panel" id="privacyPanel">
    <span class="label">What the AI sees:</span>
    <pre id="privacyContent"></pre>
  </div>
  <div class="file-bar" id="fileBar"></div>
  <div class="input-area">
    <div class="input-row">
      <button class="attach-btn" onclick="document.getElementById('fileInput').click()" title="Attach file">&#128206;</button>
      <input type="file" id="fileInput" style="display:none" accept=".txt,.md,.csv,.json,.xml,.pdf,.docx,.doc,.pptx,.ppt,.xlsx,.xls,.py,.js,.ts,.sql,.html,.log,.yaml,.yml" multiple onchange="handleFiles(this.files)" />
      <textarea id="chatInput" placeholder="Type your message..." rows="1"></textarea>
      <button class="send-btn" id="sendBtn" onclick="send()">&#9654;</button>
    </div>
    <div class="input-footer">
      <label class="toggle"><input type="checkbox" id="showPrivacy" onchange="togglePrivacy()"> Show what AI sees</label>
      <span style="color:var(--text2)">PDF, DOCX, PPTX, XLSX, TXT, CSV, JSON + more</span>
    </div>
  </div>
</div>

<script>
const B = window.location.origin;
let apiKey = '';
let wsId = '';
let wsInfo = null;
let history = [];
let attachedFiles = []; // [{file_id, filename, size, char_count}]

function hdr() { return { 'X-API-Key': apiKey, 'Content-Type': 'application/json' }; }
function toast(m,t='') { const e=document.createElement('div'); e.className='toast '+t; e.textContent=m; document.body.appendChild(e); setTimeout(()=>e.remove(),3000); }
function esc(s) { const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }

function fileIcon(name) {
  const ext = name.split('.').pop().toLowerCase();
  const icons = {pdf:'&#128196;',docx:'&#128196;',doc:'&#128196;',pptx:'&#128202;',ppt:'&#128202;',xlsx:'&#128202;',xls:'&#128202;',csv:'&#128202;',json:'&#128203;',xml:'&#128203;',txt:'&#128196;',md:'&#128196;',py:'&#128187;',js:'&#128187;',ts:'&#128187;',sql:'&#128187;',html:'&#127760;'};
  return icons[ext] || '&#128196;';
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB';
  return (bytes/1024/1024).toFixed(1) + ' MB';
}

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
    const llm = document.getElementById('llmBadge');
    if (wsInfo.llm && wsInfo.llm.configured) { llm.textContent=wsInfo.llm.provider; llm.className='badge badge-green'; llm.style.display='inline'; }
    else { llm.textContent='No LLM'; llm.className='badge badge-orange'; llm.style.display='inline'; }
    document.getElementById('chatInput').focus();
  } catch(e) { toast('Connection error','error'); }
}

document.getElementById('authKey').addEventListener('keydown', e => { if(e.key==='Enter') login(); });

// File upload
async function handleFiles(fileList) {
  for (const file of fileList) {
    if (file.size > 20*1024*1024) { toast(file.name+' too large (max 20MB)','error'); continue; }

    // Add chip in uploading state
    const tempId = 'temp_'+Date.now()+'_'+Math.random();
    attachedFiles.push({_tempId:tempId, filename:file.name, size:file.size, uploading:true});
    renderFileBar();

    // Upload
    const form = new FormData();
    form.append('file', file);
    try {
      const r = await fetch(B+'/v1/upload', {
        method:'POST',
        headers:{'X-API-Key':apiKey},
        body:form
      });
      if (!r.ok) {
        const err = await r.json();
        toast('Upload failed: '+(err.detail||'error'),'error');
        attachedFiles = attachedFiles.filter(f => f._tempId !== tempId);
        renderFileBar();
        continue;
      }
      const data = await r.json();
      // Replace temp entry with real data
      const idx = attachedFiles.findIndex(f => f._tempId === tempId);
      if (idx >= 0) {
        attachedFiles[idx] = {file_id:data.file_id, filename:data.filename, size:data.size, char_count:data.char_count};
      }
      renderFileBar();

      // Show file in chat
      addFileMessage(data.filename, data.size, data.char_count);
      toast(file.name+' ready','success');
    } catch(e) {
      toast('Upload error: '+e.message,'error');
      attachedFiles = attachedFiles.filter(f => f._tempId !== tempId);
      renderFileBar();
    }
  }
  document.getElementById('fileInput').value = '';
}

function renderFileBar() {
  const bar = document.getElementById('fileBar');
  if (attachedFiles.length === 0) { bar.className='file-bar'; bar.innerHTML=''; return; }
  bar.className = 'file-bar active';
  bar.innerHTML = attachedFiles.map((f,i) => `
    <div class="file-chip ${f.uploading?'uploading':''}">
      <span class="file-icon">${fileIcon(f.filename)}</span>
      <span class="file-name">${esc(f.filename)}</span>
      <span class="file-size">${formatSize(f.size)}${f.char_count?' / '+f.char_count+' chars':''}</span>
      ${f.uploading?'':`<button class="file-remove" onclick="translateFile(${i})" title="Translate" style="color:var(--accent2)">&#127760;</button><button class="file-remove" onclick="removeFile(${i})" title="Remove">&times;</button>`}
    </div>
  `).join('');
}

function removeFile(idx) {
  attachedFiles.splice(idx,1);
  renderFileBar();
}

// Translation
async function translateFile(idx) {
  const f = attachedFiles[idx];
  if (!f || !f.file_id) return;
  const lang = prompt('Translate to which language?', 'French');
  if (!lang) return;

  addMessage('system', 'Translating '+f.filename+' to '+lang+'...');

  try {
    const r = await fetch(B+'/v1/translate', {
      method:'POST', headers:hdr(),
      body:JSON.stringify({file_id:f.file_id, language:lang})
    });
    const d = await r.json();
    if (!r.ok) { addMessage('system','Translation error: '+(d.detail||'failed')); return; }

    // Show download link
    const el = document.createElement('div');
    el.className = 'msg-file';
    el.innerHTML = `<span class="fi">&#128196;</span><div class="fd"><span class="fn">${esc(d.filename)}</span><span class="fs">${d.paragraphs_translated} paragraphs translated</span></div><a href="${B}${d.download_url}" target="_blank" style="color:var(--accent2);text-decoration:none;font-size:13px;margin-left:8px">Download</a>`;
    document.getElementById('messages').appendChild(el);
    scrollBottom();
    toast('Translation complete!','success');
  } catch(e) { addMessage('system','Error: '+e.message); }
}

function addFileMessage(name, size, chars) {
  const el = document.createElement('div');
  el.className = 'msg-file';
  el.innerHTML = `<span class="fi">${fileIcon(name)}</span><div class="fd"><span class="fn">${esc(name)}</span><span class="fs">${formatSize(size)} / ${chars} characters extracted & anonymized</span></div>`;
  document.getElementById('messages').appendChild(el);
  scrollBottom();
}

// Drag & drop
const chatContainer = document.getElementById('chatContainer');
['dragenter','dragover'].forEach(ev => {
  document.body.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); });
});
document.body.addEventListener('drop', e => {
  e.preventDefault(); e.stopPropagation();
  if (e.dataTransfer.files.length && apiKey) handleFiles(e.dataTransfer.files);
});

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

  const typingEl = document.createElement('div');
  typingEl.className = 'typing';
  typingEl.innerHTML = '<span></span><span></span><span></span>';
  document.getElementById('messages').appendChild(typingEl);
  scrollBottom();

  history.push({role:'user', content:text});

  // Collect file_ids
  const file_ids = attachedFiles.filter(f=>f.file_id).map(f=>f.file_id);

  try {
    if (document.getElementById('showPrivacy').checked) {
      const anonR = await fetch(B+'/v1/anonymize', {method:'POST', headers:hdr(), body:JSON.stringify({text, workspace_id:wsId})});
      if (anonR.ok) { const anonD = await anonR.json(); showPrivacyView(anonD.anonymized_text); }
    }

    const r = await fetch(B+'/v1/chat/completions', {
      method:'POST', headers:hdr(),
      body: JSON.stringify({workspace_id:wsId, messages:history, model:'default', file_ids})
    });

    typingEl.remove();
    sendBtn.disabled = false;

    if (!r.ok) {
      const err = await r.json();
      addMessage('system', 'Error: '+(err.detail||'Something went wrong'));
      return;
    }

    const data = await r.json();
    const reply = data.choices?.[0]?.message?.content || '(empty response)';
    history.push({role:'assistant', content:reply});
    addMessage('assistant', reply);

  } catch(e) {
    typingEl.remove();
    sendBtn.disabled = false;
    addMessage('system', 'Error: '+e.message);
  }
}

function addMessage(role, text) {
  const el = document.createElement('div');
  el.className = 'msg msg-'+role;
  if (role === 'assistant') {
    let html = esc(text);
    html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    html = html.replace(/`([^`]+)`/g, '<code style="background:var(--bg);padding:2px 4px;border-radius:3px">$1</code>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\n/g, '<br>');
    el.innerHTML = html;
  } else { el.textContent = text; }
  document.getElementById('messages').appendChild(el);
  scrollBottom();
}

function scrollBottom() { const m=document.getElementById('messages'); m.scrollTop=m.scrollHeight; }

function togglePrivacy() {
  document.getElementById('privacyPanel').classList.toggle('active', document.getElementById('showPrivacy').checked);
}

function showPrivacyView(text) {
  const el = document.getElementById('privacyContent');
  let html = esc(text).replace(/\[PRODUCT_\d+\]/g,'<span class="placeholder-ppi">$&</span>').replace(/&lt;[A-Z_]+_\d+&gt;/g,'<span class="placeholder-pii">$&</span>');
  el.innerHTML = html;
}

const chatInput = document.getElementById('chatInput');
chatInput.addEventListener('input', function(){autoResize(this)});
chatInput.addEventListener('keydown', function(e){ if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();} });
function autoResize(el) { el.style.height='auto'; el.style.height=Math.min(el.scrollHeight,200)+'px'; }
</script>
</body>
</html>
"""
