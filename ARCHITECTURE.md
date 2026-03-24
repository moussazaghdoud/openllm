# SecureLLM — Integration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CUSTOMER APPLICATIONS                           │
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐   │
│  │ /chat    │   │ /portal  │   │ Backend  │   │ Mobile App   │   │
│  │ (Web UI) │   │ (Admin)  │   │ (API)    │   │ (API client) │   │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └──────┬───────┘   │
│       │              │              │                 │            │
│       └──────────────┴──────────────┴─────────────────┘            │
│                              │                                      │
│                    X-API-Key: slm_xxx                               │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│              SECURELLM PRIVACY GATEWAY (FastAPI)                    │
│              openllm-production.up.railway.app                      │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 AUTHENTICATION LAYER                        │   │
│  │  X-API-Key → workspace_id (per-request isolation)          │   │
│  │  X-Admin-Key → SaaS admin operations                       │   │
│  └─────────────────────────┬───────────────────────────────────┘   │
│                            │                                        │
│  ┌─────────────────────────▼───────────────────────────────────┐   │
│  │              OBSERVABILITY MIDDLEWARE                        │   │
│  │  Request tracing (X-Request-ID) │ Metrics │ Audit logging   │   │
│  └─────────────────────────┬───────────────────────────────────┘   │
│                            │                                        │
│  ┌─────────────────────────▼───────────────────────────────────┐   │
│  │            PRIVACY PIPELINE (mandatory, no bypass)          │   │
│  │                                                             │   │
│  │  ┌─────────────────┐    ┌─────────────────────────────┐    │   │
│  │  │  WAVE 1: PPI    │    │  WAVE 2: PII (Presidio)     │    │   │
│  │  │                 │    │                               │    │   │
│  │  │ Per-workspace   │───▶│ NLP-based detection:         │    │   │
│  │  │ proprietary     │    │ • PERSON → <PERSON_1>        │    │   │
│  │  │ terms database  │    │ • EMAIL → <EMAIL_ADDRESS_1>  │    │   │
│  │  │                 │    │ • PHONE → <PHONE_NUMBER_1>   │    │   │
│  │  │ "OmniSwitch" →  │    │ • CREDIT_CARD, IBAN, IP     │    │   │
│  │  │ [PRODUCT_1]     │    │ • LOCATION, DATE_TIME        │    │   │
│  │  └─────────────────┘    └─────────────────────────────┘    │   │
│  │                                                             │   │
│  │  Mapping stored in Redis (opaque mapping_id returned)       │   │
│  └─────────────────────────┬───────────────────────────────────┘   │
│                            │                                        │
│  ┌─────────────────────────▼───────────────────────────────────┐   │
│  │                    API ENDPOINTS                             │   │
│  │                                                             │   │
│  │  POST /v1/anonymize         → anonymize text                │   │
│  │  POST /v1/deanonymize       → restore from mapping_id       │   │
│  │  POST /v1/chat/completions  → anonymize→LLM→deanonymize    │   │
│  │  POST /v1/upload            → extract+anonymize document    │   │
│  │  POST /v1/translate         → translate preserving layout   │   │
│  │  POST /v1/translate/async   → background translation job    │   │
│  │  GET  /v1/jobs/{id}         → poll job status               │   │
│  │  GET  /v1/download/{id}     → download translated file      │   │
│  └─────────────────────────┬───────────────────────────────────┘   │
│                            │                                        │
│  ┌─────────────────────────▼───────────────────────────────────┐   │
│  │               OUTPUT SANITIZER                              │   │
│  │  • Check for residual placeholders                          │   │
│  │  • Detect leaked sensitive patterns (IBAN, CC)              │   │
│  │  • Log warnings for data leak incidents                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────────┐  │
│  │ Admin UI / │  │ Customer     │  │ Chat UI /chat        │  │
│  │ Dashboard   │  │ Portal       │  │ + file attachment    │  │
│  │ /           │  │ /portal      │  │ + translation        │  │
│  └──────────────┘  └───────────────┘  └────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
              ┌────────────────┼─────────────────┐
              ▼                ▼                  ▼
┌──────────────────┐ ┌──────────────┐  ┌──────────────────────┐
│  Redis           │ │  Presidio    │  │  LLM Upstream        │
│  (Railway)       │ │  (built-in)  │  │  (per-workspace)     │
│                  │ │              │  │                      │
│ • Mappings       │ │ • spaCy NLP  │  │ • Anthropic API      │
│ • Workspace data │ │ • Entity     │  │ • OpenAI API         │
│ • API keys       │ │   detection  │  │ • OpenClaw Gateway   │
│ • File buffers   │ │              │  │ • Custom endpoint    │
│ • Job state      │ │              │  │                      │
│ • Audit log      │ │              │  │ Only anonymized data │
│ • Stats          │ │              │  │ reaches this layer   │
└──────────────────┘ └──────────────┘  └──────────────────────┘
```

## Data Flow: Chat Completion

```
1. User sends message
   "Pierre Dupont from SNCF called about TGV InOui delays"

2. Auth: X-API-Key → workspace_id (tenant isolation)

3. Wave 1 (PPI): workspace-specific terms replaced
   "Pierre Dupont from [PRODUCT_1] called about [PRODUCT_2] delays"

4. Wave 2 (PII): Presidio NLP detection
   "<PERSON_1> from [PRODUCT_1] called about [PRODUCT_2] delays"

5. Mapping stored: mapping_id → Redis
   { "<PERSON_1>": "Pierre Dupont", "[PRODUCT_1]": "SNCF", "[PRODUCT_2]": "TGV InOui" }

6. Anonymized message → upstream LLM (Anthropic/OpenAI/etc.)
   LLM sees ONLY placeholders, never real data

7. LLM responds with placeholders:
   "<PERSON_1> should contact [PRODUCT_1] support about [PRODUCT_2] schedule"

8. Output sanitized: check for residual placeholders, leaked patterns

9. Deanonymize using mapping_id:
   "Pierre Dupont should contact SNCF support about TGV InOui schedule"

10. Clean response returned to user
```

## Data Flow: Document Translation

```
1. User uploads report.docx via POST /v1/upload
   → Text extracted from XML (<w:t> tags)
   → Anonymized and stored (file_id returned)
   → Raw bytes stored for translation (base64)

2. User requests POST /v1/translate {file_id, language: "French"}

3. Text paragraphs extracted from DOCX XML
   → Image paragraphs (<w:drawing>, <w:pict>) SKIPPED
   → Empty paragraphs SKIPPED

4. Paragraphs sent to LLM in chunks of 15
   → Each chunk: numbered paragraphs → JSON array response
   → 3-minute timeout per chunk

5. Original DOCX rebuilt via zipfile:
   → word/document.xml: <w:t> text replaced with translations
   → First <w:t> in each paragraph gets translated text
   → Subsequent <w:t> tags cleared
   → ALL other files (images, styles, rels) copied unchanged

6. Translated DOCX stored → download URL returned
```

## Multi-Tenant Isolation

```
Workspace A (SNCF)          Workspace B (Airbus)
├── PPI: TGV, Transilien    ├── PPI: A320, Beluga
├── LLM: Anthropic          ├── LLM: OpenAI
├── API key: slm_aaa...     ├── API key: slm_bbb...
├── Stats: 1,247 anon       ├── Stats: 892 anon
├── Mappings: map:A:*       ├── Mappings: map:B:*
└── Files: file:A:*         └── Files: file:B:*

No cross-workspace access possible.
API key resolves to exactly one workspace.
```

## API Contract Examples

### Anonymize
```bash
POST /v1/anonymize
X-API-Key: slm_xxx

{"text": "John Smith, john@acme.com", "workspace_id": "abc123"}

→ {"anonymized_text": "<PERSON_1>, <EMAIL_ADDRESS_1>", "mapping_id": "map:abc123:def456"}
```

### Chat Completion (privacy proxy)
```bash
POST /v1/chat/completions
X-API-Key: slm_xxx

{
  "workspace_id": "abc123",
  "messages": [{"role": "user", "content": "Summarize Pierre's email"}],
  "file_ids": ["file:abc123:xyz789"]
}

→ {"choices": [{"message": {"content": "Pierre's email discusses..."}}]}
```

### Translate Document
```bash
POST /v1/translate
X-API-Key: slm_xxx

{"file_id": "file:abc123:xyz789", "language": "French"}

→ {"filename": "report_translated_French.docx", "download_url": "/v1/download/dl:abc123:qqq", "paragraphs_translated": 42}
```
