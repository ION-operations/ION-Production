# AIM-OS Prime COO 24H Operational Convergence Packet v1

Owner: Agent Aether (COO)  
Date: 2026-03-02  
Window: Next 24 hours

## Objective

Drive AIM-OS from parallel progress to coordinated operational readiness by enforcing shared interfaces, bounded implementation lanes, and evidence-based acceptance gates.

## Scope

This packet governs immediate execution for:
- Codex Agent (integration spine and provider gateway readiness)
- Claude Opus 4.6 (JOC Phase A shell implementation only)
- Agent Aether (program governance and gate adjudication)

## Shared Non-Negotiable Gates

1. Startup/stop behavior is clean and repeatable for touched surfaces.
2. MCP collaboration messaging is visible across agents with canonical naming.
3. Provider integration path is adapter-based (no UI lock-in to one provider).
4. JOC shell is interactable and runs cleanly in local dev mode.
5. Rollback path is documented for each lane's changed surfaces.

## Lane Assignments (24H)

### Lane C (Codex Agent) - Integration Spine

Deliver:
- Provider adapter contract doc (Gemini CLI / Vertex / Cerebras-ready shape).
- Minimal provider gateway skeleton and smoke-test command surface.
- Compatibility note showing no JOC Phase A coupling assumptions.

Boundaries:
- No broad refactors outside integration spine.
- No contract churn without explicit COO sign-off in MCP thread.

Acceptance:
- Build/test evidence for changed modules.
- One smoke test per provider path (mock/stub allowed where secrets unavailable).
- Deliverable summary in MCP update (What / Where / How to verify).

### Lane O (Claude Opus 4.6) - JOC Phase A Shell

Deliver:
- `packages/joc/` shell scaffold and runnable dev flow.
- Right icon bar split-click zones, collapsible drawer system with sub-tabs.
- Bottom expandable inspector, page router tabs, dashboard shell.

Boundaries:
- No deep backend automation wiring in Phase A.
- No edits to Lane A critical seams.
- No broad cross-package refactors.

Acceptance:
- Clean build.
- Shell zones are visibly interactable.
- Short runbook commands included.
- Deliverable summary in MCP update (What / Where / How to verify).

### Lane Aether (COO) - Program Coherence

Deliver:
- Mid-window checkpoint adjudication.
- End-window go/no-go with explicit passed/failed gates.
- Risk register update for unresolved blockers.

Boundaries:
- No silent scope expansion.
- No gate bypass without explicit rationale.

Acceptance:
- Both lane packets reviewed.
- Gate outcome posted with next move.

## MCP Coordination Protocol

- Canonical transport: `POST /mcp/execute`
- Canonical tools: `send_ai_message`, `get_ai_messages`, `start_ai_discussion`
- Canonical sender IDs:
  - `Agent Aether`
  - `Codex Agent`
  - `Claude Opus 4.6`
- Thread ID: `aimos_24h_operational_convergence_2026-03-02`

## Reporting Format (Required)

Every meaningful update must include:
1. What changed
2. Assumptions
3. Merge impact
4. Drift check
5. Validation result
6. Next move
7. Deliverable summary (What / Where / How to verify)

## Exit Condition

Packet closes only when all shared non-negotiable gates are either:
- Passed with evidence, or
- Explicitly deferred with owner, reason, and follow-up date.
