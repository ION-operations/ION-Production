# Composer Audit 002 — Code Verification & Message Store

**Date:** 2026-03-03  
**Scope:** AUDIT_001 findings verification, BAS/JOC code trace, mcp_ai_messages.json validity  
**Classification:** For Braden only

---

## 1. Executive Summary

- **AUDIT_001 P0 (screenshot) CORRECTED:** basClient uses `GET /api/browser/screenshot` and converts blob→base64. No POST viewport. Finding #1 was incorrect or outdated.
- **CONFIRMED:** `mcp_ai_messages.json` is invalid JSON — truncated at `ai_msg_4_20260303_123346` (content field empty, file ends mid-object).
- **CONFIRMED:** ExtractResponseResponse.metadata drift — BAS returns `{ totalResponses, index, selector }`; basClient type has `{ index?, provider?, tokensEstimate? }`. Optional fields; runtime may work but type is incomplete.
- **BrowserStatus / ProviderInfo:** Current basClient types align with BAS. No isConnected; ProviderInfo uses counts. AUDIT_001 P1 findings appear resolved or were misreported.

---

## 2. Screenshot Flow Verification

**basClient.getScreenshot()** (packages/joc/src/services/basClient.ts:257–272):
- Calls `GET ${BAS_API}/browser/screenshot?browserId=X&type=png`
- Fetches raw blob, converts to base64 via btoa()
- Returns string for `<img src="data:image/png;base64,...">`

**BAS api/browser.ts** (lines 88–115):
- `GET /api/browser/screenshot` returns raw image (res.send(screenshot))
- Content-Type: image/png or image/jpeg

**Conclusion:** Seam is correct. No POST viewport. Finding #1 was wrong.

---

## 3. Message Store Validation

**Test:** `node -e "JSON.parse(require('fs').readFileSync('mcp_ai_messages.json','utf8'))"`  
**Result:** `INVALID: Unexpected end of JSON input`

**File state:** Truncated at line 3119. Last entry:
```json
{
  "message_id": "ai_msg_4_20260303_123346",
  "from_ai": "gemini",
  "to_ai": "Codex Agent",
  "content": 
```
(Content field empty; file ends abruptly.)

**Impact:** Any tool that reads mcp_ai_messages.json via JSON.parse will fail. Codex agents, get_ai_messages merge logic, and guidance retrieval are affected.

**Backup:** `backups/mcp_ai_messages.json.bak_20260303_124326` exists. May be usable for repair.

---

## 4. Contract Alignment Summary

| Endpoint / Type | basClient Expectation | BAS Actual | Status |
|----------------|----------------------|------------|--------|
| GET /api/browser/screenshot | Blob → base64 | Raw image | ✅ Aligned |
| GET /api/browser/status | { success, status } | ✅ | ✅ Aligned |
| GET /api/bridge/providers | { name, inputSelectors, submitSelectors, responseSelectors, url } | ✅ | ✅ Aligned |
| POST /api/bridge/extract-response | metadata?: { index?, provider?, tokensEstimate? } | metadata: { totalResponses, index, selector } | ⚠️ Partial drift |
| POST /api/bridge/send-prompt | { success, response?, duration? } | { success, response?, duration? } | ✅ Aligned |

---

## 5. E2E Smoke Test Alignment

**packages/joc/scripts/bas-e2e-smoke.mjs:**
- Gates 1–6: Health, Launch, Navigate, Screenshot, Status, Providers
- Uses same endpoints as basClient: `/api/browser/screenshot`, `/api/browser/status`, `/api/bridge/providers`
- No POST viewport. Correct.

---

## 6. Recommendations (For Braden)

1. **Immediate:** Repair `mcp_ai_messages.json` — truncate to last valid entry (ai_msg_3) or restore from backup, then validate parse.
2. **Governance:** Update AUDIT_001 and FINDINGS_MASTER_LIST: mark Finding #1 as corrected (screenshot seam OK); retain Finding #5 (message store) as confirmed.
3. **Optional:** Extend basClient ExtractResponseResponse.metadata type to include `totalResponses`, `selector` for full parity.

---

## 7. Deliverable Summary

- **What:** Second Composer audit — code verification of BAS/JOC seam, message store validation.
- **Where:** `docs/Composer/AUDIT_002_2026-03-03_CODE_VERIFICATION_AND_MESSAGE_STORE.md`
- **How to verify:** Run `node -e "JSON.parse(require('fs').readFileSync('mcp_ai_messages.json','utf8'))"` (expect INVALID until repaired); read basClient.ts lines 257–272 for screenshot flow.
