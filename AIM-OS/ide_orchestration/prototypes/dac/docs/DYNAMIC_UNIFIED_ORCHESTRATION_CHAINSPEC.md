---
id: "dynamic_unified_orchestration_chainspec"
type: "chain_spec"
title: "Dynamic Unified Orchestration (DUO) ChainSpec"
description: "Phased ChainSpec + quality gates for MCP + REST dual integration"
author: "codex"
version: "v0.1.0"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
status: "draft"
tags: ["orchestration", "chain_spec", "quality_gates", "aim-os"]
confidence: 0.85
---

# Dynamic Unified Orchestration (DUO) ChainSpec

**Purpose:** Translate the research corpus (North Star/Unified Textbook, Aether Chat, EPIC orchestration, Prompt Chains meta/execution) into an executable ChainSpec + gate system that governs the dual-integration effort (MCP + REST) for AIM-OS.

**Scope:** Entire AIM-OS integration stack (Python core ↔ MCP server ↔ REST API ↔ IDE/DAC experience). Applies to every agent during Phase 3 consolidation and onward.

---

## dYZ_ ChainSpec Summary

```yaml
epic:
  id: "dynamic_unified_orchestration"
  version: "0.1.0"
  objective: "Enable MCP + REST dual integrations with shared quality gates and telemetry"
  phases:
    - id: "phase_0_research_alignment"
      status: "complete"
    - id: "phase_1_dual_integration_foundations"
      dependencies: ["phase_0_research_alignment"]
    - id: "phase_2_system_wiring"
      dependencies: ["phase_1_dual_integration_foundations"]
    - id: "phase_3_experience_enablement"
      dependencies: ["phase_2_system_wiring"]
    - id: "phase_4_quality_readiness"
      dependencies: ["phase_3_experience_enablement"]
  workstreams:
    - id: "ws_mcp_path"
    - id: "ws_rest_path"
    - id: "ws_shared_services"
    - id: "ws_experience"
    - id: "ws_quality_telemetry"
```

Each phase has **entry gates** (preconditions) and **exit gates** (deliverables + metrics). Gate telemetry is persisted in **CMC**, indexed by **HHNI**, validated by **VIF/SDF-CVF**, and remediated through **APOE** chain actions.

---

## dY"< Workstream Definitions

| Workstream | Objective | Systems | Primary Owners |
| --- | --- | --- | --- |
| `ws_mcp_path` | Ensure existing MCP server + tools are production-grade (tool list parity, health checks, retry/circuit breakers) | `lucid_mcp_server.py`, MCP tool registry, Command Server (Cursor) | Alex + Codex |
| `ws_rest_path` | Stand up AIM-OS REST surface (FastAPI skeleton, auth, gating) and parity endpoints to MCP tools | New REST service (FastAPI), Python packages | Alex + Codex |
| `ws_shared_services` | Shared abstractions (MCPService, REST clients, retry/backoff, logging, timeline) | Shared TS services, Python orchestrators, CMC/TCS | Alex + Nova + Codex |
| `ws_experience` | IDE/DAC integrations (hooks, panels, sandbox UI, orchestration UI) | React panels, hooks, CMC timeline UI | Sage + Nova |
| `ws_quality_telemetry` | Quality gates, VIF telemetry dashboards, SEG synthesis, audit trails | VIF, SEG, TCS dashboards, HHNI indexes | Aether + Sev + Codex |

---

## dY`< Phase Definitions + Gates

### **Phase 0 – Research & Alignment (Complete)**
- **Objective:** Consolidate orchestration knowledge (59+ docs) and align on dual-path strategy.
- **Entry Gate:** NA (initial phase).
- **Exit Gate:** Research corpus logged on coordination board, standards confirmed (Aether acknowledgment).

### **Phase 1 – Dual Integration Foundations**
- **Objective:** Establish reliable MCP tooling and REST scaffolding in parallel.
- **Entry Gates:**
  - Research sweep recorded (`Codex [RESEARCH COMPLETE]` entry).
  - MCPService health + retry specs accepted.
  - REST architecture decision recorded (FastAPI baseline).
- **Exit Gates:**
  - MCP path: `mcp_lucid-mcp_*` tools enumerated with pass/fail status; Command Server heartbeat + circuit breaker metrics stored in CMC.
  - REST path: FastAPI service skeleton with `/health`, `/version`, `/mcp/execute` parity endpoint stub + auth middleware.
  - Shared services: ChainSpec templates + gate registry checked into repo.

### **Phase 2 – System Wiring**
- **Objective:** Wire AIM-OS core systems to both paths.
- **Entry Gates:** Phase 1 exit gates + Aether approval on ChainSpec.
- **Exit Gates:**
  - MCP path: Each priority tool (CMC, HHNI, VIF, APOE, SEG, CAS, TCS) verified via automated tests (`MCPService.test.ts` + script outputs).
  - REST path: Equivalent REST endpoints return real data for the same 7 systems with documented payloads.
  - Shared services: Type-safe clients + hooks updated to auto-select MCP/REST based on availability.
  - Telemetry: VIF confidence + SEG evidence persisted per call.

### **Phase 3 – Experience Enablement**
- **Objective:** Integrate dual paths into IDE/DAC (hooks, panels, sandbox).
- **Entry Gates:** Phase 2 exit gates + UI readiness (Sage components ready, Nova hooks ready).
- **Exit Gates:**
  - Hooks: `useAIMOS`, `useICIP`, sandbox hooks toggle between MCP/REST with zero mock data.
  - Panels: System Index, Timeline, Aether Chat use real data from either path.
  - Orchestration UI: Chain execution telemetry visible (Gate status, VIF confidence).

### **Phase 4 – Quality & Launch Readiness**
- **Objective:** Ensure production readiness with automated gates.
- **Entry Gates:** Phase 3 exit gates + consolidated documentation.
- **Exit Gates:**
  - Testing: Integration + E2E suites cover MCP + REST flows (CI evidence stored in CMC).
  - Quality: VIF confidence ≥ 0.9 for critical flows; SDF-CVF quality reports signed.
  - Documentation: L0-L4 stacks + API docs for both paths; ChainSpec + gate registry versioned.
  - Launch decision: APOE plan `duo_launch_readiness` executed with PASS status.

---

## dYs? Quality Gate Registry (Excerpt)

| Gate ID | Layer | Description | Success Metrics | Remediation |
| --- | --- | --- | --- | --- |
| `gate_reality_check` | Phase 1 Entry | Research + chain spec approved | Board entry references + Aether ack | Repeat verification audit |
| `gate_mcp_tools` | Phase 1 Exit | MCP tools enumerated + pass tests | 8/8 priority tools pass CLI tests | APOE task `fix_mcp_tool` |
| `gate_rest_scaffold` | Phase 1 Exit | REST skeleton responds w/ auth | `/health` 200, `/version` matches commit | Roll back + patch |
| `gate_dual_system` | Phase 2 Exit | MCP + REST respond for 7 systems | `ATLAS_CMC_ATOM_SCHEMA.md` + `AGENT_NEXUS_RELATIONSHIP_MAPPING.md` + gate tuple (`prompt_gate_evidence_1763155979.847537`, `9868db52-1191-44a4-95d8-8ce21425796f`, `evidence_4329e66d64f1`) proving atom/evidence parity | Auto-create remediation chain |
| `gate_cas_monitoring_phase2` | Phase 2 Telemetry | CAS monitoring of TCS timeline is documented + linked | Chronos + Meta publish integration doc + board acknowledgment | Re-open Chronos/Meta audit |
| `gate_system_map_integrity` | Phase 3 Entry | Timeline nodes land in SEG with CMC atom_id/witness_id mapping | `CHRONOS_TCS_SEG_TIMELINE_MAPPING.md` + Nexus tuple (`prompt_gate_evidence_1763155979.847537`, `9868db52-1191-44a4-95d8-8ce21425796f`, `evidence_4329e66d64f1`) produced by `packages/seg/tests/test_priority1_end_to_end.py` | Re-run ingest + mapping review |
| `gate_ui_reality` | Phase 3 Exit | IDE uses real data (no mocks) | Telemetry log shows `mock=false`, user tests pass | Block release until data verified |
| `gate_launch_readiness` | Phase 4 Exit | Quality + docs complete | All preceding gates PASS, SDF-CVF score ≥ 0.9 | APOE `launch_blocker` plan |

All gate outcomes recorded in CMC (`collections/gates`) with bitemporal fields (`valid_from`, `valid_to`) and indexes via HHNI for rapid lookup. SEG synthesizes gate history; dashboards use VIF for confidence overlays.

---

## dY"S Gate Evidence Snapshot (2025-01-27)

| Gate | Status | Evidence | Notes |
| --- | --- | --- | --- |
| `gate_cas_monitoring_phase2` | PASS | `ide_orchestration/prototypes/dac/docs/agents/chronos/CHRONOS_TCS_CAS_INTEGRATION.md` + board entry `Codex [COORDINATION AUDIT] 2025-01-27` | CAS confirmed as separate monitoring system with documented flows; telemetry ready for CMC ingest. |
| `gate_system_map_integrity` | PASS | `CHRONOS_TCS_SEG_TIMELINE_MAPPING.md` + Nexus tuple (`prompt_gate_evidence_1763155979.847537`, `9868db52-1191-44a4-95d8-8ce21425796f`, `evidence_4329e66d64f1`) + `packages/seg/tests/test_priority1_end_to_end.py` run (2025-11-14). | Gate evidence recorded on board (`Codex [GATE UPDATE] 2025-11-14`) and Nexus journal; rerun the ingest script if telemetry drifts. |
| `gate_dual_system` | PASS | `ATLAS_CMC_ATOM_SCHEMA.md`, `AGENT_NEXUS_RELATIONSHIP_MAPPING.md`, tuple above proving shared atom/evidence IDs. | Board entry + MemoryStore artifacts in `test_data_priority1/` retain the tuple for audits; regenerate if Atlas rotates schemas. |

---

## dYOY Telemetry & Remediation Flow

1. **Execution:** Hook/service call emits telemetry (path, system, duration, result) via MCP/REST clients.
2. **Storage:** Telemetry + gate outcomes stored in CMC with chain_instance_id.
3. **Indexing:** HHNI indexes telemetry docs keyed by phase/workstream/gate.
4. **Evaluation:** VIF calculates confidence; SDF-CVF enforces thresholds.
5. **Remediation:** APOE plan `duo_gate_failure` auto-enqueues tasks (retry, escalate, document).
6. **Reporting:** Dashboards (IDE panels) show ChainSpec progress + gate status; board updated for major transitions.

---

## dY"< Implementation Notes

- **ChainSpec Artifacts:** Keep YAML/JSON definitions in `orchestration/chains/`. Use templates for phases/workstreams/tasks to avoid drift.
- **Automation Scripts:** Extend existing `test-command-server.ts` to hit both MCP + REST endpoints and push results into gate registry.
- **Documentation Sync:** Whenever gates change, update `DYNAMIC_UNIFIED_ORCHESTRATION_CHAINSPEC.md` and reference in board messages (bitemporal principle).
- **Collaboration:** All structural edits coordinated with @Aether; append-only updates on coordination board.

---

**Status:** Draft ChainSpec ready for review  
**Next:** Review with @Aether, then begin filling gate registry + implementation tasks for Phase 1.
