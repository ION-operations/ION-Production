# COMPOSER Aether OS Migration Classification — 2026-03-13

**Author:** COMPOSER  
**Role:** Auditor-Mapper  
**Packet:** AETHER-COMPOSER-01  
**Status:** Complete  
**Scope:** AIM-OS repository at `C:\Users\bombe\Desktop\AIM-OS` — classification for Aether OS migration

---

## Executive Summary

This report classifies the AIM-OS repository so migration can begin without folklore. Every significant subsystem, document set, and directory is tagged as `canonical`, `runtime-real`, `staging`, `evidence`, `sediment`, or `deprecated`. Executives can now point to a first migration list without guessing what is alive vs dead.

---

## 1. Directory-Level Classification Table

| Directory | Classification | Rationale |
|-----------|----------------|-----------|
| **.agent** | canonical | Active governance: genomes, comms, sev packets, status, workflows. Constitutional layer. |
| **.agent/cache** | evidence | Generated audit data; useful for verification, not steering. |
| **.agent/comms** | canonical | Chat, inbox, broadcasts, status, tasks — coordination truth. |
| **.agent/genomes** | canonical | Agent genomes (sev, opus, codex, composer, gemini, antigravity, aether). Governing identity. |
| **.agent/sev** | canonical | CEO packets, reports, activation briefs, mission packets. Executive command. |
| **.agent/runtime** | staging | Codex CLI forge; partially integrated. |
| **.agent/workflows** | canonical | Deploy workflows, agent procedures. |
| **.agent/trails** | evidence | Session trails; audit trail, not canon. |
| **.agent/file_indexes** | evidence | Generated indexes; not constitutional. |
| **.agent/mission_reports** | evidence | Historical reports; proof, not steering. |
| **.cursor** | runtime-real | Cursor rules, skills, modes. Active IDE host config. |
| **.claude** | runtime-real | Claude host config. |
| **.github** | canonical | Workflows (quintet-gate), governance automation. |
| **config** | runtime-real | quintet_gate_policy.json, runtime config. |
| **docs** | mixed | See Section 2. |
| **Documentation** | sediment | Alternate doc tree; likely duplicate. |
| **Documentation_Consolidated** | sediment | Consolidated copy; may overlap docs/. |
| **legacy_docs** | deprecated | Historical; does not migrate. |
| **packages** | mixed | See Section 3. |
| **scripts** | runtime-real | MCP control, HTTP fallback, AI engine, launchers. Active execution. |
| **PROJECT_TRUTH** | canonical | Evidence ledger, canonical indexes. Audit truth. |
| **knowledge_architecture** | canonical | SAM, SUPER_INDEX, system maps. Atlas layer. |
| **mcp-aether** | staging | Aether MCP; being built. |
| **mcp_memory** | runtime-real | Memory persistence; CMC/HHNI data. |
| **test_mcp_configs** | evidence | Test configs; verification. |
| **test_mcp_memory** | evidence | Test memory; verification. |
| **archive** | deprecated | Historical; does not migrate. |
| **backups** | deprecated | Do not migrate. |
| **forensics_backups** | deprecated | Do not migrate. |
| **snapshots** | evidence | Point-in-time captures; 90_evidence. |
| **audit** | evidence | Audit outputs. |
| **audits** | evidence | Audit outputs. |
| **evidence** | evidence | Proof artifacts; 90_evidence. |
| **reports** | evidence | Generated reports. |
| **achievements** | sediment | Historical; not steering. |
| **active_work** | staging | Work in progress. |
| **analysis** | evidence | Analysis outputs. |
| **artifacts** | evidence | Build/output artifacts. |
| **benchmarks** | evidence | Benchmark data. |
| **bootloaders** | staging | Bootstrap systems; partial. |
| **builds** | evidence | Build outputs. |
| **codex** | runtime-real | Codex host adapter. |
| **codex-systems** | staging | Codex subsystems; partial. |
| **codex_workspace** | evidence | Workspace state. |
| **context_capsule_wire_and_mapper_v1** | sediment | Shadow context; Tier B prototype. AUDIT_01: reject as canon. |
| **coordination** | evidence | Coordination state. |
| **cursor-addon** | runtime-real | Cursor MCP addon; spawns lucid_mcp_server. |
| **daemon_rag_system** | runtime-real | RAG daemon MCP; specialized, not primary. |
| **data** | evidence | Data stores. |
| **deployment** | staging | Deployment configs. |
| **diagnostics** | evidence | Diagnostic outputs. |
| **echo-forge-loop** | runtime-real | App; Echo Forge Loop. |
| **examples** | evidence | Example code. |
| **forcing_test_flip** | sediment | Test artifact; not steering. |
| **goals** | canonical | Goal tracking; governance. |
| **htmlcov** | evidence | Coverage reports. |
| **IDE** | runtime-real | Tauri IDE; context_mapper live seam. |
| **ideas** | sediment | Idea capture; not canon. |
| **ide_orchestration** | staging | Prototypes (DAC); not runtime. |
| **images** | evidence | Image assets. |
| **north_star_project** | sediment | Historical; superseded by .agent/SEV_NORTH_STAR. |
| **orchestration_templates** | staging | Templates; partial. |
| **organized_root_files** | sediment | Organizational; not steering. |
| **plans** | evidence | Planning artifacts. |
| **projects** | evidence | Project state. |
| **runs** | evidence | Run outputs. |
| **schema** | runtime-real | Schema definitions. |
| **schemas** | runtime-real | Schema packages. |
| **src** | runtime-real | Source code. |
| **state** | evidence | State files. |
| **Testing** | evidence | Test artifacts. |
| **tests** | runtime-real | Test suite. |
| **test_data_priority1** | evidence | Test data. |
| **test_data_priority1_format** | evidence | Test data. |
| **test_data_priority1_linkage** | evidence | Test data. |
| **tmp** | deprecated | Temporary; exclude. |
| **ui** | staging | UI components; partial. |
| **UIeditor** | staging | Editor UI; partial. |

---

## 2. docs/ Classification (Grouped by Topic)

### Canonical

| Document | Purpose |
|----------|---------|
| `MCP_RUNBOOK.md` | Launch canon; Codex HTTP fallback, transport truth. |
| `CONTEXT_CANON.md` | Single entry point for context-system truth (DEC-007). |
| `CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md` | Full context registry. |
| `roundtable/IDENTITY_CANON.md` | Agent identity and lanes. MANDATORY. |
| `roundtable/decisions/DECISION_LOG.md` | Frozen decisions. |
| `roundtable/OPUS_READ_FIRST.md` | Roundtable entry. |
| `roundtable/README.md`, `START_HERE.md` | Roundtable navigation. |
| `GENOME_INJECTION_PROTOCOLS_BY_PLATFORM.md` | Genome injection truth. |
| `GENOME_ARCHITECTURE_BASE_PLUS_OVERLAY.md` | Genome architecture. |
| `CODEX_IDE_MCP_ONBOARDING_V1.md` | Codex onboarding. |
| `GETTING_STARTED.md` | Entry point. |
| `ARCHITECTURE_OVERVIEW.md` | High-level architecture. |
| `AIMOS_MAJOR_SYSTEMS.md` | Major systems index. |

### Runtime-Real (Operational Reference)

| Document | Purpose |
|----------|---------|
| `AUDIT_01_SYSTEM_MAP.md` | 10-plane system map; verified 2026-03-05. |
| `AUDIT_02_CAPABILITY_MATRIX.md` | Capability matrix. |
| `AUDIT_03_MCP_TOOL_AUDIT.md` | MCP tool audit. |
| `AUDIT_04_COMPARATIVE_LANDSCAPE.md` | Comparative landscape. |
| `JOC_MASTER_PLAN.md` | JOC planning. |
| `JOC_UI_REQUIREMENTS.md` | JOC requirements. |

### Evidence (90_evidence)

| Document Set | Purpose |
|--------------|---------|
| `roundtable/decisions/DEC-*` | Frozen decision packets. |
| `communications_mcp_down/*` | MCP-down recovery threads. |
| `Composer/audits/*` | Composer audit outputs. |
| `agent_reports/*` | Agent reports. |
| `phase2b_context_packet/*` | Context packet snapshot. |
| `INCIDENT_*` | Incident records. |
| `RECOVERY_STATUS_BOARD_*` | Recovery status. |
| `SALVAGE_PLAN_*` | Salvage plans. |
| `BRADEN_HANDOFF_*` | Handoff records. |

### Sediment (Danger Zone)

| Document | Risk |
|----------|------|
| `agents/ROLE_CONTINUITY_CANON.md` | **DEPRECATED** — Superseded by IDENTITY_CANON. Pre-handoff roles (Aether=CEO). Looks authoritative. |
| `SevCEO.txt` | Valuable doctrine but source text, not live canon. MASTER_ANALYSIS: "not live canon." |
| `THE SOVEREIGN CONTEXT MAPPER.txt` | Massive design doc; may contain stale paths. |
| `UserInterface.txt` | Historical. |
| `Polycast.txt` | Historical. |
| `aiosv1.txt` | Historical. |

---

## 3. packages/ Classification (Key Packages)

### Runtime-Real (Active, Verified)

| Package | Purpose | Dest |
|---------|---------|------|
| `joc` | JOC app; command surface. | 30_cockpit/joc |
| `antigravity-extension` | Antigravity IDE extension. | 20_habitats/antigravity |
| `browser-automation-service` | BAS on :5002. | 10_runtime/bridges |
| `jarvis_injector` | Window injector. | 10_runtime or 30_cockpit |
| `ai_collaboration` | AI-to-AI messaging. | 10_runtime/messaging |
| `cmc_service` | Context Memory Core. | 10_runtime/memory |
| `hhni` | HHNI retrieval. | 10_runtime/retrieval |
| `vif` | Verifiable Intelligence Framework. | 10_runtime/security |
| `apoe` | Orchestration engine. | 10_runtime/orchestration |
| `context_bootloader` | Context loader. | 10_runtime |
| `nl_tags` | NL tagging. | 10_runtime/retrieval |
| `router` | APOE-MCP router. | 10_runtime/orchestration |
| `llm_client` | LLM client. | 10_runtime |
| `ide_chat_app` | IDE chat app. | 40_product/chat |

### Staging (Partial, Owner + Gate Required)

| Package | Status |
|---------|--------|
| `joc-tournament` | Tournament builds; Palisade, etc. Staging. |
| `mcp_server` | FastAPI MCP; port conflict with SSE. Needs deprecation or role clarity. |
| `lucid_mcp_server` | Package; root `lucid_mcp_server.py` is canonical. Package may be tool modules. |
| `timeline_context_system` | Tier D; do not promote until dedupe. |
| `knowledge_architecture` | Atlas; canonical but large. |

### Sediment / Deprecated

| Package | Rationale |
|---------|-----------|
| `mcp_server` (if obsolete) | Port conflict with SSE; alternate architecture. Verify before deprecation. |

---

## 4. Source Code Classification

### Canonical Entry Points

| Path | Role |
|------|------|
| `lucid_mcp_server.py` (root) | Primary MCP server; 103 tools; stdio JSON-RPC. |
| `scripts/mcp_http_fallback_server.py` | HTTP bridge :5001; Codex REQUIRED. |
| `scripts/mcp_sse_server.py` | SSE for ChatGPT :8000. |
| `scripts/mcp_control.ps1` | MCP control; `ensure`, `test`. |
| `scripts/ai_engine/*` | AI engine pipeline; Chain Director, Agent Spawner, etc. |

### Runtime-Real Scripts

| Script | Purpose |
|--------|---------|
| `scripts/mcp_control.ps1` | MCP launch/recovery. |
| `scripts/launchers/LAUNCH_JARVIS.*` | JOC launcher. |
| `scripts/launchers/START_WINDOW_INJECTOR.ps1` | Window injector. |
| `scripts/launchers/start_codex_agent.ps1` | Codex agent. |
| `scripts/check_mcp_tool_parity.py` | Tool parity verification. |

---

## 5. First-Pass Canonical Migration Candidates (Phase 0)

Migrate first into `00_governance`:

| Source | Dest |
|--------|------|
| `.agent/SEV_NORTH_STAR.md` | 00_governance/doctrine |
| `.agent/OPUS_NORTH_STAR.md` | 00_governance/doctrine |
| `.agent/genomes/*` | 00_governance/agents |
| `.agent/sev/AETHER_OS_EXECUTIVE_MIGRATION_PACKET_2026-03-13.md` | 00_governance/packets |
| `.agent/sev/AETHER_OS_GIT_GITHUB_GOVERNANCE_PACKET_2026-03-13.md` | 00_governance/packets |
| `.agent/sev/MASTER_ANALYSIS_AND_CONSOLIDATION_PROGRAM_2026-03-13.md` | 00_governance/packets |
| `docs/roundtable/IDENTITY_CANON.md` | 00_governance/doctrine |
| `docs/roundtable/decisions/DECISION_LOG.md` | 00_governance/decisions |
| `docs/CONTEXT_CANON.md` | 00_governance/doctrine |
| `docs/MCP_RUNBOOK.md` | 00_governance/doctrine |
| `PROJECT_TRUTH/00_evidence_ledger.md` | 00_governance/atlas |
| `.agent/AIMOS_MASTER_SYSTEM_INDEX.md` | 00_governance/atlas |
| `.agent/SYSTEM_REGISTRY.md` | 00_governance/atlas |
| `knowledge_architecture/` (curated) | 00_governance/atlas |
| `.agent/comms` (structure) | 00_governance (comms doctrine) |
| `.agent/CEO_DIRECTIVE_PERMANENT.md` | 00_governance/doctrine |

---

## 6. First-Pass Runtime-Real Migration Candidates (Phase 1–2)

### Phase 1 — Minimal Runtime Kernel

| Source | Dest |
|--------|------|
| `lucid_mcp_server.py` | 10_runtime/kernel |
| `scripts/mcp_http_fallback_server.py` | 10_runtime/bridges |
| `scripts/mcp_sse_server.py` | 10_runtime/bridges |
| `scripts/mcp_control.ps1` | 10_runtime or scripts |
| `packages/cmc_service/` | 10_runtime/memory |
| `packages/hhni/` | 10_runtime/retrieval |
| `packages/ai_collaboration/` | 10_runtime/messaging |
| `packages/vif/` | 10_runtime/security |
| `mcp_memory/` | 10_runtime/memory (data path) |
| `cursor-addon/` | 20_habitats/cursor |
| `packages/antigravity-extension/` | 20_habitats/antigravity |
| `packages/browser-automation-service/` | 10_runtime/bridges |

### Phase 2 — Host Cards and Launchers

| Source | Dest |
|--------|------|
| `scripts/launchers/*` | 20_habitats/launchers |
| `codex/` | 20_habitats/codex |
| `docs/CODEX_IDE_MCP_ONBOARDING_V1.md` | 20_habitats/host_cards |
| `docs/GENOME_INJECTION_PROTOCOLS_BY_PLATFORM.md` | 20_habitats/host_cards |

---

## 7. Danger-Zone Register (Sediment That Looks Authoritative)

| Artifact | Location | Risk | Action |
|----------|----------|------|--------|
| **ROLE_CONTINUITY_CANON** | `docs/agents/ROLE_CONTINUITY_CANON.md` | Deprecated 2026-03-05. Pre-handoff roles. Conflicts with IDENTITY_CANON. | Tag DEPRECATED; do not migrate. |
| **SevCEO.txt** | `docs/SevCEO.txt` | Valuable doctrine; MASTER_ANALYSIS says "not live canon." | Classify as evidence; extract doctrine into canon if needed. |
| **THE SOVEREIGN CONTEXT MAPPER.txt** | `docs/THE SOVEREIGN CONTEXT MAPPER.txt` | 10K+ lines; may have stale paths (context_capsule, DAC). | Audit before use; treat as sediment. |
| **packages/mcp_server** | `packages/mcp_server/server.py` | Port :8000 conflict with SSE. Alternate architecture. | Resolve role; deprecate or document as specialized. |
| **context_capsule_wire_and_mapper_v1** | Root | Shadow context; AUDIT_01: "Reject as canon." | Do not migrate as canon. |
| **Documentation** / **Documentation_Consolidated** | Root | Duplicate doc trees. | Classify; likely sediment. |
| **north_star_project** | Root | Superseded by `.agent/SEV_NORTH_STAR.md`. | Do not migrate. |
| **Old branch docs** | `docs/GIT_UPDATE_*` | Point to `codexgit-mcp-fallback-offline-comms`; branch reality differs. | Evidence only; align with current branch. |

---

## 8. Recommended Migration Order (Phase 0 — Constitutional)

1. **North stars** — `.agent/SEV_NORTH_STAR.md`, `.agent/OPUS_NORTH_STAR.md`
2. **Genomes** — `.agent/genomes/*` (sev, opus, codex, composer, gemini, antigravity, aether)
3. **Comms doctrine** — `docs/roundtable/IDENTITY_CANON.md`, `docs/CONTEXT_CANON.md`, `docs/MCP_RUNBOOK.md`
4. **Command packets** — `.agent/sev/AETHER_OS_*`, `MASTER_ANALYSIS_*`
5. **Root map and migration ledger** — CODEX scaffold `ROOT_MAP.md`, `MIGRATION_LEDGER.md`
6. **Atlas** — `PROJECT_TRUTH/00_evidence_ledger.md`, `.agent/AIMOS_MASTER_SYSTEM_INDEX.md`, `.agent/SYSTEM_REGISTRY.md`
7. **Decisions** — `docs/roundtable/decisions/DECISION_LOG.md`

---

## 9. What Must Not Migrate Early

- `backups/`, `forensics_backups/`, `archive/`
- Duplicate documentation trees (`Documentation`, `Documentation_Consolidated`, `legacy_docs`)
- Old build artifacts (`builds/`, `htmlcov/`, `__pycache__`)
- Historical UI competition residue (`joc-tournament` builds until Phase 3)
- Dead launch attempts (many legacy launchers; deprecation tags missing)
- Sprawling partial experiments with no current owner
- Any document not classified against runtime truth
- `tmp/`, `.pytest_cache/`, `.venv/`

---

## 10. Acceptance Gate — Met

Executives can now point to a first migration list without guessing what is alive vs dead. This report provides:

- Directory-level classification table
- First-pass `canonical` migration candidates
- First-pass `runtime-real` migration candidates
- Danger-zone register (sediment that looks authoritative)
- Recommended migration order for Phase 0 (constitutional) items

---

**COMPOSER** | AETHER-COMPOSER-01 | Classification complete | 2026-03-13
