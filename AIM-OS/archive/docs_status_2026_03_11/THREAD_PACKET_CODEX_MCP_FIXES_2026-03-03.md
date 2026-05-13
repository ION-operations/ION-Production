# Thread Packet: Codex-MCP Fixes (2026-03-03)

Thread ID: `aimos_task_codex_mcp_fixes_2026-03-03`  
Owner: Codex-MCP  
Coordinator: Codex Agent  
Related packet: `docs/COO_ROUNDTABLE_OPERATIONAL_AUDIT_AND_EXECUTION_PLAN_V1_2026-03-03.md`

---

## Mission Objective

Stabilize the MCP operational backbone so collaboration, retrieval, and startup diagnostics are reliable under production usage.

---

## In Scope

- MCP startup/runtime reliability issues in `lucid_mcp_server.py`
- Collaboration transport health checks and fallback policy
- Retrieval-path diagnostics for `retrieve_memory`
- Message-store integrity verification and monitoring

## Out of Scope

- Broad JOC UI redesign
- Browser automation feature additions unrelated to MCP health
- Core doctrine rewrites

---

## 24h Deliverables

1. Transport health baseline
   - Confirm and document when `POST /mcp/execute` is available.
   - Provide deterministic fallback guidance when command server is offline.

2. Startup warning triage
   - Reproduce and classify:
     - RAG constructor mismatch warning
     - CMC import-path warning
   - Propose minimal patch plan with rollback notes.

3. Retrieval degradation report
   - Run targeted `retrieve_memory` probes.
   - Identify whether failure mode is index population, query path, or embedding dependency.

4. Thread heartbeat
   - Post status updates in this thread with canonical report format.

---

## 72h Deliverables

1. Patch set for highest-impact MCP reliability defects.
2. Health-check command set (one command each for transport, retrieval, collaboration visibility).
3. Drift report comparing:
   - runtime startup claims
   - `scripts/check_mcp_tool_parity.py`
   - `SOURCE_OF_TRUTH.yaml`

---

## Acceptance Gates

1. MCP transport gate
   - Either command server is consistently reachable or fallback path is operationally documented and tested.

2. Retrieval gate
   - `retrieve_memory` returns non-empty results for at least one known indexed domain query.

3. Collaboration gate
   - `get_ai_messages` for this thread returns current updates and expected count progression.

4. Evidence gate
   - Deliverable posted with:
     - what changed
     - assumptions
     - merge impact
     - drift check
     - validation result
     - next move
     - deliverable summary

---

## Validation Commands (minimum)

- `python scripts/check_mcp_tool_parity.py`
- Direct tool probes via `SimpleMCPServer`:
  - `get_ai_messages`
  - `retrieve_memory`
  - `get_memory_stats`

---

## Rollback

- Keep backup of message-store files before any migration edits.
- Isolate startup/import changes behind minimal diffs.
- Revert to last-known valid tool-call path if retrieval patches regress tool availability.

