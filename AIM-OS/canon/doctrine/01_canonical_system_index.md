# Canonical System Index

Created: 2026-03-05 03:22 ET  
Method: repo search + file inspection + runtime checks + build/test checks  
Rule: status is evidence-based, uncertainty is explicit

---

## Status Legend

- `built`: implemented and currently runnable/provable
- `part-built`: implementation exists but integration/runtime gaps remain
- `doc-only`: primarily specified in docs; no verified live path
- `unknown`: insufficient evidence

---

## Major Systems

| System | Status | Canonical Paths | Related Docs | Owner (Known) | Short Description | Redundant Rebuild Signal |
|---|---|---|---|---|---|---|
| MCP primary server | built | `lucid_mcp_server.py` | `docs/CODEX_IDE_MCP_ONBOARDING_V1.md` | Opus/Aether runtime lane (per identity canon) | Main monolith MCP tool surface (includes AI messaging/memory tools) | Yes - repeated "new MCP" discussions while monolith already present |
| MCP HTTP fallback bridge | built | `scripts/mcp_http_fallback_server.py`, `scripts/run_mcp_http_fallback.ps1` | `docs/communications_mcp_down/README.md` | Shared runtime ops | HTTP bridge exposing `/mcp/execute` on `:5001`; health verified | Yes - multiple restart/ownership collisions reported |
| Legacy MCP API server (alternate) | part-built | `packages/mcp_server/server.py` | `packages/mcp_server/README.md` | Unknown | Separate FastAPI-based MCP path on `:8000`; not current team transport | Yes - contributes to "which MCP is canonical" confusion |
| JOC (Joint Operations Center) | part-built | `packages/joc/` | `docs/OPUS1_JOC_GOALS_AND_ROADMAP.md`, `docs/JOC_MASTER_PLAN.md` | Opus (JOC lane) | React/Vite command surface; build passes; integration seams remain | Moderate - partial rewiring attempts around dispatch/session seam |
| Browser Automation Service (BAS) | built | `packages/browser-automation-service/` | `docs/OPUS1_BROWSER_SYSTEM_RUNBOOK_V1.md`, `docs/OPUS1_BROWSER_SYSTEM_VALIDATION_REPORT_V1.md` | Opus browser lane | Browser lifecycle + automation APIs on `:5002`; health/build/tests verified | Low - mostly hardening, not greenfield rebuild |
| Browser/chat integration layer | part-built | `packages/joc/src/pages/SessionPage.tsx`, `packages/joc/src/pages/DispatchPage.tsx`, `packages/browser-automation-service/src/api/mcpBridge.ts` | `docs/Composer/FINDINGS_MASTER_LIST.md`, `docs/OPUS1_BROWSER_SYSTEM_VALIDATION_REPORT_V1.md` | Opus + supporting specialists | JOC<->BAS seam hardened for browserId routing; authenticated response gates remain login-dependent | Yes - repeated seam fixes previously; now shifted to auth-gate discipline |
| Rust context mapper (live machine seam) | part-built | `IDE/src-tauri/src/context_mapper/*`, `IDE/src-tauri/src/context_service.rs` | `docs/AIM_OS_PRIME_MASTER_BLUEPRINT_TEAM_EXECUTION_V1_1.md` | Lane A (live machine authority) | Deterministic context extraction layer exists in codebase; current live validation in this session not executed | Low |
| Contextual sync / shadow sync prototype | part-built | `context_capsule_wire_and_mapper_v1/shadow_sync/*` | `docs/LANE_B_CONTEXTUAL_SYNC_CONVERGENCE_BLUEPRINT_V1.md`, `context_capsule_wire_and_mapper_v1/shadow_sync/README.md` | Lane B (shadow authority) | Additive standalone prototype with schema/emitter/tests; explicitly not live runtime seam | Moderate - risk of parallel architecture confusion |
| Timeline context system (deferred) | part-built | `packages/timeline_context_system/*` | `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`, `docs/roundtable/decisions/DEC-007_CONTEXT_SYSTEM_CONSOLIDATION_PACKET_2026-03-05.md` | Shared (deferred lane) | Broad context feature set exists but duplicate-variant noise blocks canonical promotion | High - duplicate variants can trigger false-canon rebuild behavior |
| Memory system (CMC + MCP memory persistence) | built | `packages/cmc_service/*`, `mcp_memory/`, `mcp_ai_messages.json` | `packages/cmc_service/README.md` | Unknown/Shared | Bitemporal memory services + message persistence; `get_memory_stats` returns operational stats | Low |
| Retrieval system (HHNI) | part-built | `packages/hhni/*` | `docs/MCP_HHNI_SETUP.md` | Unknown/Shared | Retrieval package exists; current MCP stats report HHNI index/retriever unavailable in active runtime | Moderate |
| Orchestration / coordination systems | built | `packages/apoe/*`, `packages/router/*`, `packages/specialist_system/*`, `scripts/offline_comms/*`, `.agent/comms/*` | `docs/roundtable/START_HERE.md`, `docs/communications_mcp_down/WRITE_POLICY.md` | Opus (integration spine), Composer (audits/indexing) | Multi-layer coordination stack: orchestration packages + offline/MCP messaging protocols | Yes - overlap between channels caused routing noise |
| Tool registry surfaces | built | `lucid_mcp_server.py` (`tools/list` + tool handlers), `scripts/check_mcp_tool_parity.py`, `scripts/mcp_transport_smoke.py` | `docs/CODEX_IDE_MCP_ONBOARDING_V1.md` | Runtime ops/shared | Tool catalog and execution routing implemented; parity proven (`103 listed = 103 callable`) | Low |
| Launch/runtime bridge stack | built | `scripts/mcp_control.ps1`, `scripts/run_mcp_http_fallback.ps1`, `scripts/launchers/START_BAS_DETERMINISTIC.ps1` | `docs/OPUS1_BROWSER_SYSTEM_RUNBOOK_V1.md` | Runtime ops/shared | Health-gated startup/stop/test surfaces for MCP and BAS are implemented | Moderate - many legacy launchers still discoverable |
| Agent protocol/genome system | part-built | `.agent/genomes/*`, `.agent/genomes/GENOME_PROTOCOL.md`, `packages/specialist_system/*` | `docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V3.md`, `knowledge_architecture/systems/agent_genome/*` | Shared | Operational identity + specialist runtime exist; dedicated `packages/agent_genome` runtime package still missing | Moderate - design/runtime split can trigger duplicate framework proposals |
| Bridge/adapters (runtime) | part-built | `IDE/src-tauri/src/daemon_bridge.rs`, `packages/mcp_rag_proxy/*`, `packages/browser-automation-service/src/api/mcpBridge.ts` | `docs/DAEMON_STDIO_MCP_AND_CONTEXT_BUS_FINDINGS.md` | Lane A + runtime ops | Multiple bridge surfaces exist; consolidation and canonical routing still sensitive | Yes - repeated bridge-path ambiguity |
| Governance system | built | `docs/roundtable/*`, `docs/communications_mcp_down/*`, `.agent/COMMS_DOCTRINE.md` | `docs/roundtable/IDENTITY_CANON.md`, `docs/roundtable/decisions/DECISION_LOG.md`, `docs/communications_mcp_down/WRITE_POLICY.md` | Shared | Active governance path exists and is in use; older role maps still exist and conflict historically | Moderate - unresolved deprecation of older role canon docs |

---

## Evidence Notes

1. Runtime checks completed this session:
- `GET http://localhost:5001/health` -> `status=ok`, `ready=true`
- `POST http://localhost:5001/mcp/execute` (`get_memory_stats`) -> success
- `GET http://localhost:5002/health` -> `status=ok`

2. Build/test checks completed this session:
- `packages/joc`: `npm run build` passed
- `packages/browser-automation-service`: `npm run build` passed
- `packages/browser-automation-service`: `npm test` passed (`4` suites / `15` tests)

3. Thread evidence of coordination drift and runtime collisions:
- `docs/communications_mcp_down/threads/THREAD_aimos_roundtable_operational_convergence_2026-03-04.md`
