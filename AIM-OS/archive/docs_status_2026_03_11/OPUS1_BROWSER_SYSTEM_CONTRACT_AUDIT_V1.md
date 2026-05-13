# OPUS1 Browser System Contract Audit v1

Status: Active  
Date: 2026-03-02  
Author: Codex  
Scope: `BrowserAutomationPanel` <-> Browser Automation Service (`:5002`)

---

## 1) Objective

Establish a single authoritative contract map between:

- frontend caller: `ide_orchestration/prototypes/dac/src/panels/BrowserAutomationPanel.tsx`
- backend service: `packages/browser-automation-service/src/api/*`

This audit is the implementation baseline for Opus1 browser/JOC completion work.

---

## 2) Panel Endpoint Usage Inventory

From `BrowserAutomationPanel.tsx`, panel currently calls:

- `GET /api/connections/list`
- `GET /api/scripts/list`
- `GET /api/automation/metrics`
- `GET /api/browser/screenshot?browserId={id}&type=png`
- `POST /api/browser/launch`
- `POST /api/browser/navigate`
- `GET /api/scripts/{id}`
- `POST /api/connections/{id}/load-session`
- `POST /api/automation/execute`
- `GET /api/automation/status?executionId={id}`
- `POST /api/automation/pause`
- `POST /api/automation/resume`
- `POST /api/automation/stop`
- `POST /api/browser/close`
- `POST /api/browser/detect-elements`
- `GET /api/browser/viewport?browserId={id}`

---

## 3) Backend Endpoint Inventory

From `packages/browser-automation-service/src/api/*`:

### Browser router
- `POST /api/browser/launch`
- `POST /api/browser/navigate`
- `GET /api/browser/screenshot`
- `GET /api/browser/status`
- `POST /api/browser/close`
- `GET /api/browser/viewport`
- `POST /api/browser/detect-elements`

### Automation router
- `POST /api/automation/execute`
- `GET /api/automation/status`
- `POST /api/automation/pause`
- `POST /api/automation/resume`
- `POST /api/automation/stop`
- `GET /api/automation/metrics`

### Scripts router
- `POST /api/scripts/save`
- `GET /api/scripts/list`
- `GET /api/scripts/{id}`
- `DELETE /api/scripts/{id}`

### Connections router
- `POST /api/connections/save`
- `GET /api/connections/list`
- `GET /api/connections/{id}`
- `POST /api/connections/{id}/load-session`
- `POST /api/connections/{id}/save-session`
- `POST /api/connections/{id}/verify-session`
- `POST /api/connections/{id}/update-cookies`
- `DELETE /api/connections/{id}`

---

## 4) Contract Match Matrix

## 4.1 Matched now

All panel-required routes listed in Section 2 are now present in backend routers.

## 4.2 Behavioral caveats (still important)

1. `GET /api/browser/viewport`
   - Exists and now defaults to screenshot fallback (`viewportUrl: null`) unless a proxy template is configured.
   - Live iframe mode is only enabled when backend returns an embeddable HTTP(S) URL.
   - Optional env for proxy wiring: `BROWSER_AUTOMATION_VIEWPORT_HTTP_TEMPLATE`.

2. Automation control semantics
   - `pause/resume/stop` operate at action boundaries (cooperative control).
   - A long single action cannot be preempted mid-step yet.
   - Status payload now includes structured error details (`message` + category) instead of opaque `{}` error objects.

3. Execution state durability
   - In-memory execution map is reset on backend restart.
   - No persistent execution journal yet.

---

## 5) Hardening Applied in This Pass (Codex)

The following high-impact contract fixes were applied:

1. **Async execution start contract**
   - `POST /api/automation/execute` now starts execution in background and returns `executionId` immediately.
   - This aligns with panel polling model (`/automation/status`).

2. **Execution control plumbing**
   - Script engine now honors pause/stop checks between actions and before retries.

3. **Frontend polling stability**
   - Panel now clears `executionId` on terminal states (`completed`/`error`) to prevent repeated terminal logs.
   - Progress math now guards division-by-zero.

4. **Backend compile health**
   - TypeScript build now passes for `packages/browser-automation-service` (`npm run build` succeeded).

5. **`scriptId` execute contract**
   - `POST /api/automation/execute` now supports `scriptId`-only requests by loading saved scripts from backend script storage.
   - This removes the previous blocker requiring full inline script payload for every execution request.

---

## 6) Priority Fix Order for Opus1

## P0 (critical, do first)

1. Validate end-to-end launch -> execute -> status -> stop flow from JOC/Panel with real backend.
2. Decide viewport strategy:
   - Option A: build true viewport proxy/stream endpoint and wire `BROWSER_AUTOMATION_VIEWPORT_HTTP_TEMPLATE`.
   - Option B: keep screenshot-first as primary and treat iframe live mode as optional/non-authoritative.

## P1 (high)

1. Session reliability pass (save/load/update cookies across restarts).
2. Provider-specific login/session validity checks (ChatGPT/Gemini focused).
3. Improve status/error payload consistency across remaining non-automation routers.

## P2 (medium)

1. Execution metrics enrichment (duration histograms, per-provider stats).
2. Element inspector quality improvements (selector confidence tuning).
3. Add focused integration tests for panel-driven endpoint sequences.

---

## 7) Recommended First Implementation Slice for Opus1

Implement viewport strategy decision as first concrete slice:

- If proxy route is chosen, define explicit endpoint and payload contract.
- If screenshot-first is chosen, simplify panel live-view toggle semantics and remove ambiguity.

This is the biggest user-facing clarity gap remaining.

---

## 8) Validation Checklist (for Opus1 handoff)

Run and record:

1. `GET /health`
2. launch browser, navigate, screenshot, close
3. execute script and poll status to terminal state
4. execute saved script via `scriptId` only and poll status
5. pause/resume/stop behavior on multi-step script
6. account list + load-session + save-session/verify-session path
7. viewport path behavior and fallback behavior

Document pass/fail and attach exact command traces.

---

## 9) Current Proof Snapshot (Codex pass)

Completed in this pass:

1. Build validation
   - Command: `npm run build` (in `packages/browser-automation-service`)
   - Result: pass (`tsc` success).

2. Health endpoint smoke
   - Server started via `BrowserAutomationServer` programmatic start.
   - `GET /health` returned `status: ok`.

3. Async execution contract smoke
   - `POST /api/automation/execute` returned immediate `executionId`.
   - `GET /api/automation/status?executionId=...` returned running, then terminal error after retries for invalid `browserId` (expected behavior for this synthetic case).

4. Session and `scriptId` smoke
   - `POST /api/connections/:id/save-session` and `POST /api/connections/:id/verify-session` returned success in live endpoint smoke.
   - `POST /api/automation/execute` with `scriptId` only returned immediate `executionId`, then terminal status with structured error payload for synthetic invalid `browserId` case.

---

## 10) Merge Classification

- **Safe now**
  - Contract audit doc updates
  - Endpoint compatibility and compile fixes in browser service
  - Frontend polling terminal-state fix
- **Safe later**
  - Viewport proxy architecture
  - Session durability extensions
- **Not safe yet**
  - Any change that entangles browser mission with core kernel/context/daemon sovereignty seams

---

## 11) Drift Check

- No Lane A core seam rewrite performed.
- Mapper/daemon/kernel sovereignty preserved.
- Work remains in browser-system scope (panel + browser service integration).
- Convergence/checkpoint doctrine remains unchanged.
