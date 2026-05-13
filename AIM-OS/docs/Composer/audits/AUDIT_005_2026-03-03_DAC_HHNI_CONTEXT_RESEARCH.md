# Composer Audit 005 — DAC, HHNI, Context Research

**Date:** 2026-03-03  
**Scope:** DAC browser panel, HHNI retrieve_memory fallback chain, context attachment contract, viewport semantics  
**Classification:** For Braden only

---

## 1. Executive Summary

- **DAC Browser Panel:** Uses BAS correctly — `GET /api/browser/screenshot`, `GET /api/browser/viewport`. Falls back to screenshot mode when viewport returns null. API_BASE_URL = localhost:5002/api. Aligned.
- **HHNI retrieve_memory:** Three-tier fallback — TwoStageRetriever (IndexLevel) → basic HHNI query → simple_text_search (CMC list_atoms + substring match). Degradation path documented; simple_text_search is last resort.
- **Context attachment:** THREAD_PACKET_CODEX_CONTEXT_CONTRACT defines ContextAttachmentV0. JOC ContextCapsule is stub; adapter mapping pending. Codex-Context owns contract; Opus consumes.
- **Viewport:** BAS getViewportUrl returns null unless BROWSER_AUTOMATION_VIEWPORT_HTTP_TEMPLATE env set. DAC/JOC use screenshot fallback. By design.

---

## 2. DAC Browser Panel

**Location:** `ide_orchestration/prototypes/dac/src/panels/BrowserAutomationPanel.tsx`

**BAS integration:**
- Screenshot: `fetch(\`${API_BASE_URL}/browser/screenshot?browserId=${browserId}&type=png\`)` → localhost:5002/api/browser/screenshot
- Viewport: `fetch(\`http://localhost:5002/api/browser/viewport?browserId=${browserId}\`)` → expects `{ viewportUrl }`
- Fallback: When viewportUrl null or invalid, uses screenshot mode. Logs "Using screenshot mode (backend viewport not available)".

**Status:** Correct. No seam breakage.

---

## 3. HHNI retrieve_memory Fallback Chain

**Location:** `lucid_mcp_server.py` retrieve_memory (lines ~2867–3070)

**Flow:**
1. **TwoStageRetriever** (IndexLevel, DVNS physics) — preferred path
2. **Basic HHNI query** (IndexLevel.PARAGRAPH) — if TwoStageRetriever fails
3. **simple_text_search** — CMC list_atoms(1000), case-insensitive `query in content`

**Log messages:**
- "HHNI TwoStageRetriever failed, falling back to simple search"
- "HHNI basic query failed, falling back to simple search"
- Response includes `"method": "simple_text_search"` when fallback used

**Impact:** When HHNI/IndexLevel fails (e.g. empty index, import error), retrieval degrades to substring match. Lower quality but functional. JOC Context Web would see this if wired.

---

## 4. Context Attachment Contract

**Doc:** `docs/THREAD_PACKET_CODEX_CONTEXT_CONTRACT_2026-03-03.md`

**Proposed ContextAttachmentV0:**
- context_id, slice_type, title, content, token_estimate, confidence
- provenance: source_system, source_ref, captured_at, hash?
- truncation?: applied, policy, original_tokens

**JOC ContextCapsule (DispatchPage):**
- id, type, label, source?, tokens?
- Simpler; no provenance, confidence, truncation

**Gap:** Adapter needed. Thread packet specifies compatibility map and 72h deliverable for `packages/shared/contextAttachment.ts`. Not yet implemented.

---

## 5. Viewport Semantics

**BAS browserService.getViewportUrl:**
- Returns `null` by default (no embeddable URL)
- Returns HTTP(S) URL only if `BROWSER_AUTOMATION_VIEWPORT_HTTP_TEMPLATE` env set
- Template supports `{wsEndpoint}`, `{browserId}`

**Consumers:** DAC panel, JOC (SessionPage uses screenshot only — no viewport fetch in basClient). Both handle null correctly.

---

## 6. Recommendations (For Braden)

1. **Monitor:** HHNI retrieval quality — if simple_text_search appears frequently in logs, investigate TwoStageRetriever/HHNI index health.
2. **Track:** Codex-Context v0 contract delivery; adapter for JOC ContextCapsule when published.
3. **Optional:** Document viewport proxy architecture decision if JOC needs live embedded viewport (vs screenshot-only).

---

## 7. Deliverable Summary

- **What:** Fifth Composer audit — DAC panel alignment, HHNI fallback chain, context contract status, viewport semantics.
- **Where:** `docs/Composer/AUDIT_005_2026-03-03_DAC_HHNI_CONTEXT_RESEARCH.md`
- **How to verify:** Read BrowserAutomationPanel.tsx lines 273, 809; lucid_mcp_server.py retrieve_memory; THREAD_PACKET_CODEX_CONTEXT_CONTRACT.
