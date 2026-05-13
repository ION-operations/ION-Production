# Opus Workload Readiness Packet (2026-03-03)

Owner: Codex Agent  
Consumer: Claude Opus 4.6  
Purpose: Keep JOC lane execution unblocked by giving a clear dependency map, entry criteria, and acceptance gates.

---

## Current Opus Entry State

Unblocked now:

- BAS and JOC both compile (`npm run build` pass).
- BAS automated tests pass (`npm test` pass, 10/10 tests).
- Existing browser contract audit exists:
  - `docs/OPUS1_BROWSER_SYSTEM_CONTRACT_AUDIT_V1.md`

Blocked or risked now:

- Canonical MCP HTTP transport availability depends on command server runtime.
- Context attachment contract is not yet formalized as shared schema.
- MCP retrieval quality remains inconsistent for context-heavy queries.

---

## What Opus Can Safely Execute Immediately

1. Continue JOC surface hardening that does not change shared contracts.
2. Integrate against frozen BAS endpoints already validated in current contract docs.
3. Prepare UI adapters for context attachment using the pending v0 contract shape.

---

## Dependencies Required from Codex Threads

From `aimos_task_codex_mcp_fixes_2026-03-03`:

- Transport health statement (primary/fallback)
- Retrieval quality report and mitigation path

From `aimos_task_codex_bas_hardening_2026-03-03`:

- Confirmed endpoint shape freeze and compatibility notes
- E2E smoke evidence for ChatGPT-first flow

From `aimos_task_codex_context_contract_2026-03-03`:

- Approved `ContextAttachmentV0` schema
- Adapter map from current JOC capsule model

---

## Recommended Opus Queue (Next 24h)

1. Keep Session and Dispatch pages aligned to frozen BAS contract only.
2. Integrate context attachments through adapter layer, not ad hoc page-local schema changes.
3. Publish one E2E execution report from JOC UI path:
   - launch
   - navigate
   - screenshot
   - inject
   - extract
   - render response

---

## Recommended Opus Queue (Next 72h)

1. Replace remaining high-impact mock pages with live data paths where contracts are stable.
2. Add explicit runtime fault states:
   - BAS unavailable
   - MCP transport unavailable
   - context retrieval empty
3. Add lightweight operator runbook for JOC lane:
   - startup
   - dependency checks
   - expected telemetry
   - recovery actions

---

## Opus Acceptance Gates

1. No contract churn without thread notice and coordinator approval.
2. Build pass for touched packages before report.
3. Report format includes:
   - what changed
   - assumptions
   - merge impact
   - drift check
   - validation result
   - next move
   - deliverable summary

---

## Merge Safety Rules

- Keep changes additive and reversible.
- Do not merge context contract changes directly into multiple pages without shared adapter.
- Treat BAS/JOC seam as versioned contract, not inferred behavior.

