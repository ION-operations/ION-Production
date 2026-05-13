# AUDIT 03 - MCP Tool Quality + Safety Audit

Date: 2026-03-05
Owner: Codex
Scope: MCP tool plane quality, schemas, failure modes, auth/capability gating, logging; plus minimal Context Pack contract.

## Executive Summary

- MCP core parity is healthy: `103 listed / 103 callable` (`scripts/check_mcp_tool_parity.py`).
- ChatGPT native MCP path is active via SSE (`scripts/mcp_sse_server.py` on `:8000/sse`) with a reduced tool surface (13 tools).
- Critical interoperability defect found: SSE `send_ai_message` lacked `holder_id`, causing identity-lock failures for `Codex Agent`.
- Defect patched in source (`scripts/mcp_sse_server.py`), pending SSE process restart to activate runtime behavior.
- Overall MCP tool plane score (today): **4.0 / 5.0**.

## Post-Audit Execution Update (2026-03-05)

- SSE wrapper was restarted and smoke-validated.
- Identity-lock comms path now works for `Codex Agent` with `holder_id`.
- `context_pack_get_current` is live on SSE.
- Read-only repo evidence tools are now live on SSE:
  - `repo_read_file`
  - `repo_list_tree`
  - `repo_search`
  - `repo_diff_since`
- SSE tool count increased to **18**.

## Evidence

1. Parity check:
```json
{"listed_count":103,"callable_count":103,"parity_ok":true}
```
2. SSE live tool discovery:
```json
{"sse_tool_count":13,"tool_names":["send_ai_message","get_ai_messages","store_memory","retrieve_memory","get_memory_stats","create_plan","create_goal_timeline_node","update_goal_progress","track_confidence","add_timeline_entry","get_timeline_summary","synthesize_knowledge","get_ai_collaboration_summary"]}
```
3. SSE memory smoke test:
- `get_memory_stats` returned `success=true`, `backend=sqlite`, `status=operational`.
4. Identity-lock failure reproduced:
- `send_ai_message` from Codex identity failed with: `Identity lock mismatch ... Provide matching holder_id`.
5. Holder passthrough defect confirmed:
- SSE tool rejected `holder_id` as unexpected keyword argument.

## Canonical Tool Surfaces (Current)

- Canonical full registry: `lucid_mcp_server.py` (`tools/list`, `tools/call`) - 103 tools.
- Canonical parity guard: `scripts/check_mcp_tool_parity.py`.
- HTTP bridge (fallback): `scripts/mcp_http_fallback_server.py` (`/health`, `/mcp/list`, `/mcp/execute`).
- ChatGPT native MCP facade: `scripts/mcp_sse_server.py` (FastMCP SSE on `:8000/sse`, 13-tool subset).

## Findings (Ordered by Severity)

1. Critical - SSE sender lock incompatibility (patched in source)
- Symptom: `Codex Agent` cannot send messages over SSE when identity lock is enabled.
- Cause: SSE `send_ai_message` schema omitted `holder_id` even though delegate enforces it.
- Patch applied: `scripts/mcp_sse_server.py`
  - Added `holder_id` + `response_required` to `send_ai_message`.
  - Added `thread_id`, `content_search`, `normalize_names` to `get_ai_messages`.
- Runtime note: restart SSE server to load patch.

2. High - Transport split without explicit runtime banner
- Symptom: operators expect `:5001` but active path is `:8000/sse`.
- Risk: false outage diagnosis and duplicated recovery actions.
- Needed: one canonical runtime status doc + startup banner indicating active transport.

3. Medium - ChatGPT SSE is intentionally reduced-surface (13 tools)
- Benefit: safer/minimal external exposure.
- Risk: capability assumptions drift against 103-tool internal registry.
- Needed: explicit "external subset vs internal full set" contract doc.

4. Medium - Capability gating policy is not uniformly enforced at MCP boundary
- Current state: identity lock exists for comms sender; broad per-tool mutation caps are not centrally enforced in SSE facade.
- Needed: deny-by-default write policy for external-facing MCP sessions.

## Safety and Quality Controls Present

- Identity lock enforcement in monolith: `_validate_sender_identity_lock(...)` in `lucid_mcp_server.py`.
- Tool registry parity gate: `scripts/check_mcp_tool_parity.py`.
- HTTP fallback call logging: `data/mcp/mcp_tool_calls.jsonl` from `scripts/mcp_http_fallback_server.py`.
- Memory backend integrity reporting in `get_memory_stats`.

## Minimal Context Pack Tool Surface (Proposed)

Goal: give ChatGPT/research managers a compact, audit-safe "current truth" without exposing broad mutation actions.

### 1) `context_pack.get_current`
- Type: read-only
- Returns canonical mission state bundle.

Example response:
```json
{
  "success": true,
  "generated_at": "2026-03-05T10:30:00Z",
  "branch": "<git-branch>",
  "commit": "<short-sha>",
  "operational_definition": {
    "source": "context/00_operational_definition.md",
    "status": "current"
  },
  "current_truth": {
    "source": "context/01_current_truth.md",
    "highlights": ["what works", "what is blocked", "runtime transport"]
  },
  "canonical_map": {
    "source": "context/02_canonical_map.md"
  },
  "bounded_tasks": {
    "source": "context/03_tonight_plan.md",
    "top_tasks": ["P0", "P1", "P2"]
  },
  "already_built_registry": "PROJECT_TRUTH/03_already_built_registry.md",
  "canonical_doc_index": "PROJECT_TRUTH/02_canonical_doc_index.md"
}
```

### 2) `repo.read_file`
```json
{"path":"docs/BRADEN_MORNING_DIRECTIVES_2026-03-05.md","max_chars":12000}
```

### 3) `repo.search`
```json
{"query":"AUTH_READY","roots":["docs","context","PROJECT_TRUTH"],"max_results":100}
```

### 4) `repo.list_tree`
```json
{"root":"PROJECT_TRUTH","max_depth":3}
```

### 5) `repo.diff_since`
```json
{"commit":"<sha>","paths":["docs","context","PROJECT_TRUTH"]}
```

## What Is Missing for "Operational"

- SSE runtime restart with holder-aware schema active.
- Explicit external MCP capability policy (read-only vs mutation classes).
- Single canonical runtime-state endpoint/doc that states active transport (`SSE` vs `HTTP fallback`).

## Recommended Next 3 Tasks

1. Activate and verify SSE holder-aware messaging
- Restart `scripts/mcp_sse_server.py`.
- Verify `send_ai_message` succeeds for `Codex Agent` with `holder_id`.

2. Implement `context_pack.get_current`
- Read-only aggregator over `context/00..03` + `PROJECT_TRUTH` indexes.
- Add strict schema and sample payload tests.

3. Add MCP capability gates for external sessions
- Enforce deny-by-default for mutating tools on SSE transport.
- Add audit log entries for denied tool calls.

## Truth Lives Here

- Full MCP registry/call path: `lucid_mcp_server.py`
- External ChatGPT MCP path: `scripts/mcp_sse_server.py`
- HTTP fallback bridge: `scripts/mcp_http_fallback_server.py`
- Parity checker: `scripts/check_mcp_tool_parity.py`
- Directives: `docs/BRADEN_MORNING_DIRECTIVES_2026-03-05.md`
