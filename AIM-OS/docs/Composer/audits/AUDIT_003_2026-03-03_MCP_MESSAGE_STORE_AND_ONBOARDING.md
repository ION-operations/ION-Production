# Composer Audit 003 — MCP Message Store & Onboarding

**Date:** 2026-03-03  
**Scope:** MCP message store behavior, get_ai_messages merge logic, Codex onboarding, provider selector registry  
**Classification:** For Braden only

---

## 1. Executive Summary

- **Message store resilience:** MCP server degrades gracefully when `mcp_ai_messages.json` is corrupt — startup loads `[]`, `get_ai_messages` skips the file and returns Codex messages. But `send_ai_message` writing to mcp would overwrite with minimal state, losing history.
- **codex_ai_messages.json:** Valid JSON. Only root `mcp_ai_messages.json` is broken.
- **Provider selector registry:** Single source of truth at `packages/shared/providerSelectors.ts`. Both aiDrivers (JOC) and mcpBridge (BAS) import correctly. No drift.
- **Onboarding docs:** CODEX_IDE_MCP_ONBOARDING_V1 documents get_timeline_summary bug, canonical sender IDs, message file paths. OPUS1_ANTIGRAVITY notes viewport/screenshot semantics mismatch (panel vs backend).

---

## 2. Message Store Behavior

### Startup (_load_ai_messages)

| File | Parse Result | Server State |
|------|--------------|--------------|
| mcp_ai_messages.json (corrupt) | json.load fails | Backup created, `ai_messages = []` |
| mcp_ai_messages.json (valid) | OK | `ai_messages` = loaded list |

### get_ai_messages (merge)

- Reads both: `mcp_ai_messages.json`, `codex_workspace/.../codex_ai_messages.json`
- On parse failure: logs warning, skips file, continues
- **Result:** Returns messages from valid files + CMC. Corrupt mcp is skipped; Codex messages still returned.

### send_ai_message (cross-write)

- Writes to current agent file + cross-agent files
- When writing to mcp: loads mcp first. If corrupt → backup, `cross_messages = []`, append new message, overwrite
- **Risk:** Overwriting corrupt mcp with `[new_msg]` loses all prior mcp history. Backup preserves corrupt copy for repair.

---

## 3. Provider Selector Registry

**Location:** `packages/shared/providerSelectors.ts`

**Consumers:**
- `packages/joc/src/drivers/aiDrivers.ts` — imports CHATGPT_SELECTORS, GEMINI_SELECTORS, CLAUDE_SELECTORS (structured)
- `packages/browser-automation-service/src/api/mcpBridge.ts` — imports `getAllFlatSelectors()` (flat arrays)

**Shape:** PROVIDER_REGISTRY → toFlatSelectors() → { input, submit, response, thinking } arrays. mcpBridge expects this. Aligned.

---

## 4. BAS Health & Connections

| Endpoint | basClient | BAS | Status |
|----------|-----------|-----|--------|
| GET /health | checkBASHealth (BAS_BASE/health) | res.json({ status, timestamp, services }) | ✅ |
| GET /api/connections/list | getAccounts | { success, accounts } | ✅ |

BAS health does not return `uptime`; basClient type has `uptime?`. Optional; no impact.

---

## 5. Onboarding Doc Gaps

**CODEX_IDE_MCP_ONBOARDING_V1.md:**
- Canonical sender IDs: Agent Aether, Codex Agent, Claude Opus 4.6, electron-app
- Missing from list: gemini, Opus1, Antigravity (used in practice)
- get_timeline_summary bug documented ✅

**OPUS1_ANTIGRAVITY_BROWSER_SYSTEM_ONBOARDING_MISSION_V1.md:**
- Notes viewport semantics: panel calls GET viewport, backend defaults to screenshot fallback
- Different from screenshot endpoint — viewport = live URL, screenshot = image capture

---

## 6. Recommendations (For Braden)

1. **Repair mcp_ai_messages.json** before next send_ai_message to mcp — truncate to last valid entry (ai_msg_3) or restore from backup, validate parse.
2. **Optional:** Add canonical IDs (gemini, Opus1, Antigravity) to CODEX_IDE_MCP_ONBOARDING sender list with mapping to Claude Opus 4.6.
3. **Monitor:** After repair, verify send_ai_message cross-write does not re-corrupt.

---

## 7. Deliverable Summary

- **What:** Third Composer audit — MCP message store behavior, provider registry, onboarding alignment.
- **Where:** `docs/Composer/AUDIT_003_2026-03-03_MCP_MESSAGE_STORE_AND_ONBOARDING.md`
- **How to verify:** Run `node -e "JSON.parse(require('fs').readFileSync('codex_workspace/persistence/collaboration/codex_ai_messages.json','utf8'))"` (expect VALID); grep providerSelectors in mcpBridge and aiDrivers.
