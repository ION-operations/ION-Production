# Composer Audit 001 — Agent Activity & Seam Breakage

**Date:** 2026-03-03  
**Scope:** MCP message traffic, agent coordination, BAS/JOC contract alignment, identity drift  
**Classification:** For Braden only

---

## 1. Executive Summary

- **Critical:** Gemini's contract audit (ai_msg_6, ai_msg_7) identifies P0 seam breakage: `basClient.getScreenshot()` calls `POST /api/browser/viewport` expecting base64 JSON; BAS has no such endpoint. Screenshot capture from JOC SessionPage will fail.
- **High:** Multiple Codex sub-agents (Codex-BAS, Codex-MCP, Codex-Context) report truncated/malformed `mcp_ai_messages.json` and incomplete guidance retrieval. Aether reportedly repaired collaboration logs; status unclear.
- **Medium:** Sender identity drift — Opus1, Opus, Antigravity, Claude Opus 4.6, gemini used interchangeably. Canonical IDs not consistently enforced.
- **Positive:** JOC package is substantial (17 pages, basClient, SessionPage, DispatchPage, SystemAtlas). Gemini delivered ChatGPT E2E acceptance criteria + smoke test. Shared selector registry (`packages/shared/providerSelectors.ts`) created to eliminate selector drift.

---

## 2. MCP Traffic Analysis (Last 30 Messages)

### Active Agents & Threads

| Agent | Thread(s) | Role |
|-------|-----------|------|
| Agent Aether | aimos_24h_operational_convergence, discussion_Claude Opus 4.6_to_Agent Aether | COO, gatekeeper |
| Codex Agent | aimos_24h_operational_convergence | Operations lead |
| Claude Opus 4.6 / Opus1 / Antigravity | Multiple | JOC builder |
| gemini | aimos_roundtable_plan_consolidation | Auditor/assistant, Antigravity IDE |
| Codex-BAS | aimos_task_codex_bas_hardening, aimos_roundtable_plan_consolidation | BAS hardening |
| Codex-MCP | aimos_roundtable_plan_consolidation | MCP core |
| Codex-Context | aimos_roundtable_plan_consolidation | Context attachment contract |

### Critical Findings from Gemini's Audit (2026-03-03 12:38)

**P0 — Screenshot endpoint mismatch:**
- `basClient.getScreenshot()` calls `POST /api/browser/viewport` with `{ browserId, format, encoding: 'base64' }`, expects `{ success, screenshot: "<base64>" }`
- BAS has:
  - `GET /api/browser/screenshot?browserId=X&type=png` → raw Buffer (not JSON, not base64)
  - `GET /api/browser/viewport?browserId=X` → `{ viewportUrl }` (URL string, not image)
- **Impact:** Every `captureScreenshot()` from SessionPage will fail.

**P1 — BrowserStatus shape:** Client expects `{ status: { url, title, isConnected } }`; BAS returns `{ browserId, status: 'idle'|'navigating'|..., url?, title?, ... }` — no `isConnected`.

**P1 — ProviderInfo shape:** Client expects `{ id, selectors: ProviderSelectors }`; BAS `/bridge/providers` returns `{ name, inputSelectors: number, submitSelectors: number, ... }` (counts, not selector objects).

**P2 — ExtractResponseResponse.metadata:** Client expects `{ provider, tokensEstimate }`; BAS returns `{ totalResponses, index, selector }`.

### Onboarding / Store Issues

- **Codex-Context** (ai_msg_0 12:36): "mcp_ai_messages.json is malformed/truncated at ai_msg_4_20260303_123346, so guidance retrieval is incomplete."
- **Codex-BAS** (ai_msg_0 12:38): "Current readable feed contains only 2 messages, and team context appears incomplete due canonical message-store truncation."
- **Codex Agent** (ai_msg_0 12:48): "Aether has repaired the collaboration JSON logs. You can proceed on your lane now."

---

## 3. JOC Package State

**Location:** `packages/joc/`

**Key files touched by agents:**
- `src/services/basClient.ts` — 8+ methods, types for BAS API
- `src/pages/SessionPage.tsx` — BASViewport, live screenshots, inject/extract
- `src/store/sessionStore.ts` — 6 BAS live actions
- `src/pages/DispatchPage.tsx` — ContextCapsule stub, BAS integration
- `packages/shared/providerSelectors.ts` — Shared selector registry (single source of truth)
- `scripts/bas-e2e-smoke.mjs` — E2E smoke test (Gates 1–6)

**Gemini's self-reported changes (before role rebase to auditor):**
- sessionStore: launchSession, injectPrompt, extractResponse, captureScreenshot, refreshBASStatus
- SessionPage: MockBrowserViewport → BASViewport
- basClient: getScreenshot, type fixes, convenience aliases
- DispatchPage: ContextCapsule data model + pill UI

**Verification:** Gemini claims `npx tsc --noEmit` → EXIT CODE 0. Not independently verified in this audit.

---

## 4. Identity Drift

| Canonical | Observed Variants |
|-----------|-------------------|
| Claude Opus 4.6 | Opus1, Opus, Antigravity |
| Codex Agent | Codex, Codex-BAS, Codex-MCP, Codex-Context |
| Agent Aether | Aether |

Antigravity and gemini appear to be the same session (Antigravity IDE / Gemini Ultra). Opus and Antigravity both reference JOC work; unclear if same agent or handoff.

---

## 5. Git Activity

Recent commits (last 40) are predominantly:
- README / docs updates
- GPTWAVES / ProEarth / Graphics / Systems expansion
- No obvious JOC-specific commits in top 40

JOC work may be uncommitted, on a different branch, or committed under different message patterns.

---

## 6. Recommendations (For Braden)

1. **Immediate:** Verify `mcp_ai_messages.json` and `codex_workspace/persistence/collaboration/codex_ai_messages.json` are valid JSON and not truncated. If Aether repaired them, confirm repair is complete.
2. **P0:** Align basClient screenshot call with BAS — either add `POST /api/browser/screenshot` returning `{ success, screenshot: "<base64>" }` on BAS, or change basClient to use `GET /api/browser/screenshot` and convert Buffer client-side.
3. **P1:** Freeze and document BAS response shapes for BrowserStatus, ProviderInfo, ExtractResponseResponse; update basClient types to match or add adapters.
4. **Governance:** Enforce canonical sender IDs in mission packets. Add "Composer" to canonical list for audit reports.

---

## 7. Deliverable Summary

- **What:** First Composer silent audit — MCP traffic, agent activity, BAS/JOC seam breakage, identity drift.
- **Where:** `docs/Composer/AUDIT_001_2026-03-03_AGENT_ACTIVITY_AND_SEAM_BREAKAGE.md`
- **How to verify:** Read report; cross-check with `get_ai_messages`, basClient.ts, BAS api/browser.ts.
