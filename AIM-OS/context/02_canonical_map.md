# AIM-OS Canonical Map (Current)

Last updated: 2026-03-05 03:22 ET (auth-aware capsule reconciliation)
Purpose: Prevent rebuild drift and ensure external synthesis uses current canonical surfaces

## Core System Map (existing, do not duplicate)

1. Prime doctrine and sequencing
- `docs/AIM_OS_PRIME_MASTER_BLUEPRINT_TEAM_EXECUTION_V1_1.md`
- `docs/AIM_OS_PRIME_CANON_INDEX_V1.md`
- `docs/AIM_OS_PRIME_COO_24H_OPERATIONAL_CONVERGENCE_PACKET_V1.md`

2. Browser automation runtime (BAS)
- `packages/browser-automation-service/`
- API routes:
  - `src/api/browser.ts`
  - `src/api/automation.ts`
  - `src/api/connections.ts`
  - `src/api/scripts.ts`

3. JOC app surface
- `packages/joc/`
- Current primary UI runtime target for browser operations

4. MCP transport and coordination
- Fallback MCP HTTP bridge currently serving on `:5001`
- Offline comms tools:
  - `scripts/offline_comms/post_roundtable_message.py`
  - `scripts/offline_comms/post_offline_message.py`
  - `scripts/offline_comms/runtime_action_lock.py`

5. Roundtable coordination canon
- `docs/roundtable/START_HERE.md`
- `docs/roundtable/IDENTITY_CANON.md`
- `docs/roundtable/decisions/DECISION_LOG.md`
- Active thread:
  - `docs/communications_mcp_down/threads/THREAD_aimos_roundtable_operational_convergence_2026-03-04.md`

## Canonical vs Historical Docs

Use as canonical first:
- Prime blueprint + canon index docs above
- Active roundtable identity/decision docs
- Current execution packet:
  - `docs/roundtable/CODEX1_DEEP_RESEARCH_SYNTHESIS_PACKET_2026-03-05.md`

Treat as historical context unless explicitly re-authorized:
- Older salvage/recovery burst docs not referenced by current decision log
- Any role/governance claim that conflicts with `docs/roundtable/IDENTITY_CANON.md`

## Backend Systems (from Opus deep research — 68 packages)

| System | Package | Purpose |
|--------|---------|--------|
| CMC | `packages/cmc_service/` | Persistent memory store (SQLite + Qdrant) |
| HHNI | `packages/hhni/` | Hierarchical vector retrieval (TwoStageRetriever + DVNS physics) |
| VIF | (in lucid_mcp_server.py) | Verifiable Intelligence — confidence tracking |
| APOE | (in lucid_mcp_server.py) | AI-Powered Orchestration Engine — planning |
| SEG | (in lucid_mcp_server.py) | Shared Evidence Graph — knowledge synthesis |
| SDF-CVF | (in lucid_mcp_server.py) | Safety/drift detection |
| CAS | (in lucid_mcp_server.py) | Cognitive Analysis System |
| SIS/IIS | (in lucid_mcp_server.py) | Intuitive Intelligence System |

**MCP Server Monolith:** `lucid_mcp_server.py` — 10,925 lines / 548KB, parity-verified tool surface (`103 listed = 103 callable`)

## Context System Canon Tiers (DEC-007)

Canonical registry:
- `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`

Tier map:
- Tier A (live seam canonical): `IDE/src-tauri/src/context_mapper/*`, `IDE/src-tauri/src/context_service.rs`
- Tier B (staging/prototype canonical): `context_capsule_wire_and_mapper_v1/*`
- Tier S (shared support): `packages/context_bootloader/*`
- Tier D (deferred non-canonical): `packages/timeline_context_system/*`
- Tier E (evidence snapshot only): `docs/phase2b_context_packet/*`

## Do-Not-Rebuild List

Do not rebuild these from scratch; integrate and harden them:

- BAS existing API/service stack in `packages/browser-automation-service`
- JOC existing shell and buildable app in `packages/joc`
- MCP server monolith `lucid_mcp_server.py` (parity-verified `103/103` tools)
- CMC memory store `packages/cmc_service/` (SQLite + Qdrant backend)
- HHNI retrieval `packages/hhni/` (semantic search + DVNS physics)
- Existing offline roundtable messaging scripts in `scripts/offline_comms`
- Existing roundtable decision process in `docs/roundtable/decisions/DECISION_LOG.md`
- Agent genome system `.agent/genomes/`
- Military comms doctrine `.agent/COMMS_DOCTRINE.md`
- New context stacks outside DEC-007 registry tiers

## Ground Rule for ChatGPT Requests

When asking ChatGPT for plans/specs:
- include this file and `context/01_current_truth.md`
- state "integrate existing systems, do not propose greenfield rebuild"
- state "do not claim authenticated ChatGPT response readiness unless login is explicitly verified"
