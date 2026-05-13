# COO Roundtable Operational Audit and Execution Plan v1

Date: 2026-03-03  
Author: Codex Agent  
Scope: Current operational state, system fit map, production-readiness gaps, and execution plan aligned to active Codex/Opus threads.

---

## Evidence Basis

This audit is based on direct repository/runtime checks completed on 2026-03-03:

- `npm run build` in `packages/joc` (pass)
- `npm run build` in `packages/browser-automation-service` (pass)
- `npm test` in `packages/browser-automation-service` (pass, 2 suites / 10 tests)
- Port/listener checks for `5001`, `5002`, `5011` (no active listeners at audit time)
- Direct MCP tool calls via `SimpleMCPServer` (not via `POST /mcp/execute` because command server was not listening)
- Message-store parse checks for:
  - `mcp_ai_messages.json` (valid JSON, 290 entries)
  - `codex_workspace/persistence/collaboration/codex_ai_messages.json` (valid JSON, 290 entries)

---

## A) Current AIM-OS Operational State

### What is running (verified)

- JOC codebase compiles and production-builds from `packages/joc`.
- BAS compiles and test suite passes from `packages/browser-automation-service`.
- MCP tool surface is callable via direct server initialization (`SimpleMCPServer`) and returns successful responses for:
  - `get_memory_stats`
  - `get_consciousness_metrics`
  - `get_timeline_summary`
  - `get_timeline_entries`
  - `query_goal_timeline`
  - `get_autonomous_status`
  - `get_ai_collaboration_summary`
  - `retrieve_memory`

### What is partially integrated

- JOC to BAS integration is active for key client calls (`launch`, `navigate`, `status`, `screenshot`, `extract`), but broader JOC page set still contains multiple mock-driven surfaces.
- Collaboration messaging has valid mirrored files and thread filtering, but runtime is split between:
  - canonical HTTP transport (`/mcp/execute`) when command server is alive
  - direct MCP class calls when it is not.
- HHNI retrieval pipeline initializes but reports index initialization limitations; retrieval calls succeed structurally but return empty result sets for tested queries.

### What is broken or misaligned

- Canonical MCP HTTP transport is unavailable when command server is not active (no listener on `5001` during this audit).
- MCP startup reports infrastructure warnings:
  - RAG middleware constructor mismatch (`use_new_embeddings`)
  - CMC import path warning (`No module named 'cmc_service.memory_service'`)
- Collaboration appears file-backed first, with CMC-backed AI message retrieval returning zero messages in sampled runs.
- Dedicated thread initialization is incomplete:
  - `aimos_task_codex_mcp_fixes_2026-03-03`: 0 messages
  - `aimos_task_codex_context_contract_2026-03-03`: 0 messages
  - `aimos_task_codex_bas_hardening_2026-03-03`: 1 message

### MCP strengths vs weaknesses

Strengths:

- Broad callable tool surface and parity checks (`103 listed / 103 callable`).
- Dual-file message persistence improves survivability under single-file corruption.
- Tool calls remain operational even without command server when using direct MCP server execution.

Weaknesses:

- Operational dependency on extension-hosted command server for canonical HTTP path.
- Initialization warnings indicate drift between intended architecture and runtime module wiring.
- Retrieval quality is not yet consistent with expected HHNI value in planning docs.

---

## B) System Fit Map (Current Reality)

| System | Current Implementation Surface | How it Connects Today | Runtime Evidence | Main Risk |
|---|---|---|---|---|
| CMC | `packages/cmc_service`, `mcp_memory/`, `lucid_mcp_server.py` | MCP tools read/write local memory store and tags | `get_memory_stats` success; atoms present | Import-path/runtime split between legacy/local store and full CMC service |
| HHNI | `packages/hhni`, retrieval in `lucid_mcp_server.py` | Retrieval invoked through MCP (`retrieve_memory`) | Calls return success with `results=0` in sampled queries | Index not populated at runtime; degraded recall |
| VIF | `packages/vif`, gate/tracker init in MCP server | Confidence services initialized and available to tool layer | Startup logs show VIF init success | Not yet tied to hard release gates for JOC/BAS execution |
| SEG | `packages/seg`, MCP initialization hooks | Evidence graph stack initialized in MCP runtime | Startup logs show SEG init success | Evidence contracts not yet enforced across all new lanes |
| APOE | `packages/apoe` and orchestration logic | Planning/execution framework available through MCP tooling | Startup logs show ACL parser init success | Mission packets exist but thread-level execution drift persists |
| TCS | `packages/timeline_context_system` + `mcp_timeline_entries.json` | Timeline entries queried by MCP tools | `get_timeline_entries` success | Timeline quality depends on disciplined write cadence |
| CAS | `packages/cas` + MCP hooks | Cognitive metrics available through MCP | CAS init success in startup logs | Limited use as hard gate in current branch operations |
| JOC | `packages/joc` | Uses BAS + MCP-facing services/hook patterns | `npm run build` pass | Large mock/prototype surface still present |
| Browser Automation | `packages/browser-automation-service` | API consumed by JOC and DAC panel | Build + Jest pass | Runtime supervision and long-running reliability not yet locked |

---

## C) Production Readiness Gap List (Ordered by Severity)

### P0 (blocking)

1. Canonical collaboration transport is not continuously available.
   - Impact: Agent coordination cannot rely on `POST /mcp/execute` at all times.
   - Surfaces: `cursor-addon/src/commandServer.ts`, `cursor-addon/out/commandServer.js`, `scripts/launchers/LAUNCH_HYBRID_SOLUTION.ps1`

2. Codex thread activation is incomplete for the current roundtable work split.
   - Impact: MCP fixes and context-contract lanes are uninitialized in their own canonical threads.
   - Surfaces: `mcp_ai_messages.json`, `codex_workspace/persistence/collaboration/codex_ai_messages.json`

### P1 (high)

3. Retrieval quality path is degraded despite successful tool execution.
   - Impact: Context attachment and context-web features risk low-value retrieval.
   - Surfaces: `lucid_mcp_server.py`, `packages/hhni/`

4. MCP startup reports unresolved integration warnings (RAG constructor + CMC import).
   - Impact: Runtime behavior diverges from architecture assumptions and documentation.
   - Surfaces: `lucid_mcp_server.py`, `requirements.txt`, related package imports under `packages/`

5. JOC context attachment is UI-level stub, not a shared contract.
   - Impact: Opus cannot safely wire mapper outputs to dispatch attachments without churn.
   - Surfaces: `packages/joc/src/pages/DispatchPage.tsx`, `packages/joc/src/services/basClient.ts`, missing shared contract under `packages/shared/`

6. JOC has broad prototype pages beyond the validated BAS-linked path.
   - Impact: Build success can mask runtime feature incompleteness.
   - Surfaces: `packages/joc/src/pages/SynthesizerPage.tsx`, `packages/joc/src/pages/MissionBuilderPage.tsx`, `packages/joc/src/pages/SessionHealthPage.tsx`, `packages/joc/src/pages/CredentialVaultPage.tsx`

### P2 (medium)

7. Identity governance is partially normalized but still drifts across active logs.
   - Impact: Message queries and accountability become noisy.
   - Surfaces: `mcp_ai_messages.json`, `codex_workspace/persistence/collaboration/codex_ai_messages.json`, `docs/OPUS1_ANTIGRAVITY_BROWSER_SYSTEM_ONBOARDING_MISSION_V1.md`

8. Tool-count observability messaging is inconsistent across runtime logs and source-of-truth docs.
   - Impact: Reduces trust in diagnostics even when callable parity is intact.
   - Surfaces: `lucid_mcp_server.py`, `SOURCE_OF_TRUTH.yaml`, `scripts/check_mcp_tool_parity.py`

---

## D) Execution Plan

### Immediate 24h Actions

1. Activate and stabilize the three Codex task threads with explicit scope, gates, and owner.
   - Threads:
     - `aimos_task_codex_mcp_fixes_2026-03-03`
     - `aimos_task_codex_bas_hardening_2026-03-03`
     - `aimos_task_codex_context_contract_2026-03-03`

2. Lock a transport fallback policy.
   - Primary: `POST /mcp/execute` when `5001` is up.
   - Fallback: direct `SimpleMCPServer` calls with mirrored file persistence and explicit audit note.

3. Produce v0 context-attachment contract and publish to Context thread for Opus consumption.

4. Freeze BAS contract and E2E gate list for ChatGPT-first loop.

5. Publish Opus workload readiness packet with entry criteria and dependency matrix.

### Next 72h Actions

1. MCP reliability hardening.
   - Resolve startup warnings (RAG constructor mismatch, CMC import path issue).
   - Add deterministic health checks for collaboration and retrieval.

2. BAS operational hardening.
   - Validate repeated launch/navigate/inject/extract/session-save cycles.
   - Add failure-mode tests for invalid sessions and stale selectors.

3. Context contract implementation path.
   - Add shared TypeScript contract in `packages/shared/`.
   - Add adapter in JOC dispatch path and mapper output normalization.

4. Opus handoff package refresh.
   - Keep one active packet with current contract versions and acceptance gates.

### Parallelization with Claude Opus 4.6

- Codex-MCP lane and Codex-Context lane can run in parallel.
- Codex-BAS lane can run in parallel with Opus JOC UI work if BAS response shapes remain frozen.
- Opus should consume context contract only after Context lane publishes v0 schema and examples.

### Validation Gates (must pass before merge of each lane)

1. Build/test gate
   - `npm run build` for touched TS packages
   - `npm test` for BAS lane
2. MCP gate
   - `scripts/check_mcp_tool_parity.py` unchanged parity
   - `get_ai_messages` returns thread-visible updates for all three Codex threads
3. Contract gate
   - JOC and BAS agree on response shapes for screenshot/status/providers/extract metadata
4. Evidence gate
   - Report includes: what changed, assumptions, merge impact, drift check, validation, next move, deliverable summary

### Rollback Safety Checks

- Keep changes additive and isolated by lane.
- Backup collaboration files before any migration scripts touch them.
- For BAS/API changes, keep old fields until JOC consumes new fields.
- For context contract introduction, ship adapters before removing legacy fields.

