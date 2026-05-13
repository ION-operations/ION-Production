# Composer Audit 004 — Extended Investigations

**Date:** 2026-03-03  
**Scope:** DispatchPage browserId bug, jocStore vs sessionStore split, message store copies, E2E smoke, TypeScript, docs  
**Classification:** For Braden only

---

## 1. Executive Summary

- **P0 — DispatchPage browserId bug:** When no saved account, DispatchPage calls `sendPrompt({ browserId: t.session.id, ... })` where `t.session.id` is jocStore session ID (e.g. `gpt-1`, `gem-1`). BAS expects real browser IDs (`browser-1234567890-abc123`). sendPrompt will always fail in this path.
- **Store split:** sessionStore (SessionPage) has live BAS sessions with browserId. jocStore (DispatchPage) has mock fleet data with no browserId. No sync. DispatchPage cannot use sendPrompt without wiring to sessionStore or requiring accounts.
- **Message store copies:** Root `mcp_ai_messages.json` (INVALID) is canonical for MCP. `data/mcp/mcp_ai_messages.json` (VALID) exists but is not used by lucid_mcp_server.
- **E2E smoke:** Script runs; fails at Gate 1 when BAS not running (expected). No dependency issues.
- **TypeScript:** JOC and BAS both compile with `npx tsc --noEmit` (exit 0).
- **Docs:** JOC_AI_DRIVER_DESIGN.md referenced as "forthcoming" — does not exist (expected).

---

## 2. DispatchPage sendPrompt Path

**Code:** `packages/joc/src/pages/DispatchPage.tsx` lines 157–159, 196–198, 227–228

```ts
result = await sendPrompt({
    browserId: t.session.id,  // ← WRONG: 'gpt-1', 'gem-1', etc.
    prompt: ...,
    provider: t.session.provider,
    ...
});
```

**jocStore sessions:** `MOCK_SESSIONS` with `id: 'gpt-1' | 'gem-1' | 'perp-1' | 'claude-1'`  
**BAS browser IDs:** `browser-{timestamp}-{random}` from `browserService.launchBrowser`

**Impact:** Any dispatch without a saved account (fullSession path) uses sendPrompt with invalid browserId. BAS returns 404 or "browser not found".

---

## 3. sessionStore vs jocStore

| Store | Used By | Sessions | browserId |
|-------|---------|----------|-----------|
| sessionStore | SessionPage, SessionHealthPage | chatgpt-session, gemini-session | ✅ From launchSession |
| jocStore | DispatchPage, Dashboard, Drawers | gpt-1, gem-1, perp-1, claude-1 (mock) | ❌ None |

**Gap:** DispatchPage targets come from jocStore. SessionPage launches into sessionStore. No shared session model. DispatchPage cannot dispatch to SessionPage-launched browsers without unification.

---

## 4. Message Store Copies

| Path | Valid? | Used By |
|------|--------|---------|
| `mcp_ai_messages.json` (root) | ❌ Truncated | lucid_mcp_server (canonical) |
| `data/mcp/mcp_ai_messages.json` | ✅ | Not used |
| `codex_workspace/.../codex_ai_messages.json` | ✅ | lucid_mcp_server (merge) |

**Note:** `_resolve_collaboration_path("mcp_ai_messages.json")` → repo root. data/mcp copy is orphaned or legacy.

---

## 5. Build & Test Verification

| Check | Result |
|-------|--------|
| JOC `npx tsc --noEmit` | Exit 0 |
| BAS `npx tsc --noEmit` | Exit 0 |
| bas-e2e-smoke.mjs | Runs; Gate 1 fails when BAS offline (expected) |

---

## 6. Documentation

- `docs/AIM_OS_PRIME_COO_OPERATING_SCOPE_T2.md` — exists ✅
- `JOC AI Driver Design` — "forthcoming" in OPUS1_JOC_ARCHITECTURE; file does not exist (noted as future)
- CODEX_IDE_MCP related docs — paths valid

---

## 7. Additional Notes

- **System Atlas:** Uses useAIMOS → mcpClient → Command Server (port 5001). Live MCP wiring present.
- **Perplexity:** jocStore MOCK_SESSIONS includes Perplexity Pro; providerSelectors has no perplexity. Dispatch would fail with "Unsupported provider".

---

## 8. Recommendations (For Braden)

1. **P0:** Fix DispatchPage sendPrompt path — either (a) require account for all dispatch (fullSession only), or (b) wire DispatchPage to sessionStore sessions that have browserId, or (c) unify jocStore with sessionStore for BAS-backed sessions.
2. **Optional:** Use `data/mcp/mcp_ai_messages.json` as repair source if root backup is insufficient.
3. **Governance:** Document jocStore vs sessionStore split and intended unification plan.

---

## 9. Deliverable Summary

- **What:** Fourth Composer audit — DispatchPage browserId bug, store split, message copies, build verification.
- **Where:** `docs/Composer/AUDIT_004_2026-03-03_EXTENDED_INVESTIGATIONS.md`
- **How to verify:** Read DispatchPage.tsx lines 157–159; grep `browserId: t.session.id`; run `npx tsc --noEmit` in packages/joc and packages/browser-automation-service.
