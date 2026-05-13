# OPUS1 Antigravity Onboarding Mission v1

Status: Active onboarding packet  
Principal Architect: Braden (north star authority)  
Program Operations Owner: Agent Aether (COO)  
Execution Lead: Codex Agent  
Execution Specialist: Claude Opus 4.6 (Antigravity IDE)  
Coordination: Agent Aether + Codex Agent  
Date: 2026-03-02

---

## 1) Mission in One Sentence

Complete and productize the Browser System so AIM-OS supports reliable browser-based AI sessions (ChatGPT/Gemini and others), durable account/session handling, and clean automation/orchestration flow.

---

## 2) Why You Exist on This Mission

Lane A and Lane B have advanced the core runtime and shadow convergence work.  
The browser stack is now the highest-leverage gap: usable today, but not yet fully coherent as an operator-grade system.

You are authorized to focus on finishing this browser system while Codex Agent continues broader program execution.

---

## 3) Read This First (Source-of-Truth Order)

1. `docs/AIM_OS_PRIME_MASTER_BLUEPRINT_TEAM_EXECUTION_V1_1.md`
2. `docs/AIM_OS_PRIME_COO_OPERATING_SCOPE_T2.md`
3. `docs/AIM_OS_PRIME_CANON_INDEX_V1.md`
4. `docs/CHECKPOINT_D_POST_EXECUTION_CONFIRMATION_V1.md`
5. `docs/CHECKPOINT_E_ADJUDICATION_BRIEF_V1.md`
6. `docs/CHECKPOINT_E_OPEN_ITEMS_V1.md`
7. `cursor-addon/CURSOR_WEBVIEW_LIMITATION_CONFIRMED.md`
8. `packages/browser-automation-service/README.md`
9. `ide_orchestration/prototypes/dac/src/panels/BrowserAutomationPanel.tsx`
10. `IDE/src-tauri/src/webview_manager.rs`
11. `IDE/src-tauri/src/injection/injector.rs`
12. `IDE/src-tauri/src/extraction/mod.rs`
13. `IDE/src-tauri/src/state_machine/mod.rs`

---

## 4) Current Browser System Reality

## 4.1 What already works

- Tauri side can spawn and manage provider webviews (`ChatGPT`, `Gemini`) via:
  - `IDE/src-tauri/src/webview_manager.rs`
  - IPC exposure in `IDE/src-tauri/src/lib.rs`
- Prompt injection + extraction primitives exist:
  - `IDE/src-tauri/src/injection/injector.rs`
  - `IDE/src-tauri/src/extraction/mod.rs`
  - `IDE/src-tauri/src/extraction/extractor.rs`
- Browser automation backend exists and is substantial:
  - `packages/browser-automation-service/src/server.ts`
  - `packages/browser-automation-service/src/api/browser.ts`
  - `packages/browser-automation-service/src/api/connections.ts`
  - `packages/browser-automation-service/src/services/*`
- DAC browser panel exists and calls backend API:
  - `ide_orchestration/prototypes/dac/src/panels/BrowserAutomationPanel.tsx`

## 4.2 What is still incomplete

- End-to-end cohesion between panel, backend, and runtime behavior is incomplete.
- API contract behavior mismatch remains around viewport semantics:
  - panel calls `GET /api/browser/viewport?browserId=...`
  - backend defaults to screenshot fallback (`viewportUrl: null`) unless a true HTTP(S) proxy URL is configured.
- Some panel functions still use placeholders/TODO behavior (metrics and parts of element detection flow).
- Durable multi-session profile behavior needs hardening and validation.
- Browser feature path and orchestration path are not yet cleanly unified for operator-grade use.

---

## 5) Mission Scope and Boundaries

## 5.1 In scope (you own)

- Browser automation backend hardening in:
  - `packages/browser-automation-service/`
- Browser panel completion in:
  - `ide_orchestration/prototypes/dac/src/panels/BrowserAutomationPanel.tsx`
  - supporting components under `ide_orchestration/prototypes/dac/src/components/browser-automation/`
- API contract normalization between panel and backend.
- Session/account lifecycle reliability and observability.
- Validation docs and operator runbook updates for browser system.

## 5.2 Out of scope (do not touch unless explicitly authorized)

- Core Lane A critical seams:
  - `IDE/src-tauri/src/kernel_planes.rs`
  - `IDE/src-tauri/src/context_service.rs`
  - `IDE/src-tauri/src/context_mapper/*` core logic (except browser-adjacent integration if explicitly approved)
  - `IDE/src-tauri/src/daemon_bridge.rs`
- Lane B shadow convergence decision docs beyond browser-relevant references.
- Governance or gating behavior changes unrelated to browser mission.

---

## 6) Hard Constraints

1. Keep changes additive and reversible.
2. No breaking changes to existing Lane A live request behavior.
3. Do not silently redefine architecture doctrine.
4. Keep user-facing behavior understandable and testable.
5. If uncertain about a seam collision: stop and escalate to Braden + Agent Aether + Codex Agent.
6. Use COO mission-packet discipline from `docs/AIM_OS_PRIME_COO_OPERATING_SCOPE_T2.md`:
   - clear scope boundaries,
   - explicit validation proof,
   - explicit escalation triggers.
7. Use the consolidated MCP messaging rail only:
   - Canonical HTTP transport: `POST http://localhost:5001/mcp/execute`
   - Canonical tool names: `send_ai_message`, `get_ai_messages`, `start_ai_discussion` (no `mcp_lucid-mcp_` prefix)
   - Canonical sender IDs: `Agent Aether`, `Codex Agent`, `Claude Opus 4.6`, `electron-app` (pick one and stay consistent)
   - Do not use manual file-based "message board" edits as primary coordination.

---

## 7) Execution Plan (Required Sequence)

## Phase 0 - Bootstrap and Contract Audit

Deliverables:
- `docs/OPUS1_BROWSER_SYSTEM_CONTRACT_AUDIT_V1.md`

Tasks:
- Verify current API surface from `packages/browser-automation-service/src/api/*`.
- Verify current panel expectations in `BrowserAutomationPanel.tsx`.
- Produce exact mismatch table (expected endpoint vs actual endpoint).

Exit criteria:
- One authoritative mismatch table complete and reviewed.

## Phase 1 - Backend Contract Completion

Deliverables:
- Backend endpoint additions/adjustments needed to satisfy panel contract.
- Minimal docs update in `packages/browser-automation-service/README.md`.

Tasks:
- Implement missing required endpoint behavior and contract alignment (including viewport strategy or explicit replacement).
- Ensure response shapes are stable and typed.
- Add focused tests for changed/new endpoints.

Exit criteria:
- All panel-required endpoints exist and respond consistently.

## Phase 2 - Frontend Integration Completion

Deliverables:
- `BrowserAutomationPanel.tsx` updated to use stable backend contract.
- Remove placeholder paths for critical user flows.

Tasks:
- Wire launch, navigate, screenshot/live view, execute, pause/resume/stop.
- Wire account list + session load path to real backend behavior.
- Replace temporary/mock metrics with real backend-backed behavior or clearly scoped deferral.

Exit criteria:
- Operator can run primary flow without manual code patching.

## Phase 3 - Session and Reliability Hardening

Deliverables:
- Durable session behavior improvements with documented expectations.
- Error/retry behavior for common failure modes.

Tasks:
- Validate account/session save/load/update cookie loops.
- Validate restart behavior (server restart, browser reconnect expectations).
- Improve logs and status reporting for operator debugging.

Exit criteria:
- Stable behavior across repeated run cycles.

## Phase 4 - Proof and Handoff

Deliverables:
- `docs/OPUS1_BROWSER_SYSTEM_VALIDATION_REPORT_V1.md`
- `docs/OPUS1_BROWSER_SYSTEM_RUNBOOK_V1.md`

Tasks:
- Record exact commands, expected results, and observed outputs.
- Include pass/fail matrix for key browser flows.
- Include known limitations and next-step backlog.

Exit criteria:
- Another agent can reproduce success from docs only.

---

## 8) Minimum Validation Matrix

You must verify all of the following:

1. Service health
   - `GET http://localhost:5002/health` returns ok.
2. Browser lifecycle
   - launch -> navigate -> screenshot/status -> close.
3. Account/session lifecycle
   - save account -> list -> load session -> update cookies -> delete.
4. Panel integration
   - panel can launch browser, navigate, and display live/screenshot output without contract errors.
5. Automation path
   - script execute path starts and status updates are visible.
6. Error posture
   - invalid `browserId` and invalid route conditions return clean error responses.

---

## 9) Suggested Local Commands

From `packages/browser-automation-service`:

- `npm install`
- `npm run build`
- `npm start`

Quick API checks (examples):

- `GET http://localhost:5002/health`
- `POST http://localhost:5002/api/browser/launch`
- `POST http://localhost:5002/api/browser/navigate`
- `GET http://localhost:5002/api/connections/list`

Use project-standard command tooling where available in your IDE.

---

## 10) Reporting Format (Every meaningful update)

Use this exact structure:

### A. What changed
- Exact files/modules.

### B. Assumptions
- Any assumptions about runtime, environment, provider behavior.

### C. Merge impact
- Isolated / depends on live seams / future convergence risk.

### D. Drift check
- Confirm doctrine preserved.

### E. Validation result
- What was run, what passed, what failed.

### F. Next move
- Only the immediate next move.

### G. Deliverable summary
- What
- Where
- How to verify

---

## 11) Coordination Protocol

- Coordinate with Codex Agent at phase boundaries, not every micro-step.
- Keep Agent Aether informed at phase exits and when scope assumptions change.
- For AI-to-AI coordination, always use MCP collaboration tools over the consolidated transport rail.
- If the canonical endpoint is unavailable, report the transport failure explicitly and escalate (do not silently fall back to manual message files).
- Escalate immediately on:
  - seam collision risk,
  - contract ambiguity,
  - repeated unexplained failures,
  - runtime behavior changes outside mission scope.
- Keep all mission artifacts in root `AIM-OS/docs`.

---

## 12) Definition of Done for Opus1 Mission

Mission is done when:

1. Browser panel and backend contracts are aligned.
2. Manual sign-in + session reuse flow is reliable.
3. Core automation flow runs through stable APIs.
4. Validation report and runbook are complete and reproducible.
5. Changes remain additive and doctrine-safe.

---

## 13) First Action for Opus1 (Start Here)

Review and update existing `docs/OPUS1_BROWSER_SYSTEM_CONTRACT_AUDIT_V1.md` with:

- endpoint inventory from backend,
- endpoint usage inventory from panel,
- mismatch table,
- prioritized fix order (P0/P1/P2),
- first implementation slice recommendation.

Do not start broad refactors before this contract audit is current and validated.

