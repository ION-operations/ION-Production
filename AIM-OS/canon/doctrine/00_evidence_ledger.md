# Evidence Ledger - Anti-Satisficing Search Protocol

Created: 2026-03-05 02:56 ET
Branch: codexgit-mcp-fallback-offline-comms
Protocol source: GPT5.2 addendum (anti-satisficing, multi-hit, variant comparison, auditable decisions)

---

## Execution Scope

- Search roots: `packages/`, `docs/`, `scripts/`, `IDE/`, `.agent/`, `context_capsule_wire_and_mapper_v1/`, `knowledge_architecture/`
- Variant roots intentionally included for drift detection: `ide_orchestration/prototypes/dac/`, `archive/`, `snapshots/`, `apps/`
- Exclusions for core signal extraction: `**/target/**`, `**/out/**`, `**/dist/**`, `**/node_modules/**`, `**/coverage/**`
- Runtime verification refresh completed:
  - `GET http://127.0.0.1:5001/health` -> `status=ok`, `ready=true`
  - `POST http://127.0.0.1:5001/mcp/execute` (`get_memory_stats`) -> `success=true`
  - `GET http://127.0.0.1:5002/health` -> `status=ok`
- Tool parity verification refresh completed:
  - `python scripts/check_mcp_tool_parity.py` -> `listed_count=103`, `callable_count=103`, `parity_ok=true`

---

## Search Pass Template (Applied To Every Major System)

For each system, all four passes were executed:
- Pass A: direct name search
- Pass B: related concept search
- Pass C: structural search (entrypoints, registries, launchers, config)
- Pass D: drift/duplicate search (alternates, superseded, prototypes, archives)

Each system entry below includes:
- queries/terms used
- locations searched
- artifacts found
- artifacts rejected + why
- variant comparison with canon decision
- explicit uncertainty

---
## 1) MCP Server(s)

### Pass A - Direct name search
- Search target: primary MCP runtime implementations
- Queries used: `lucid_mcp_server`, `mcp_server`, `mcp_http_fallback_server`, `daemon_rag_mcp_server`
- Locations searched: repo root, `scripts/`, `packages/`, `context_capsule_wire_and_mapper_v1/`, `daemon_rag_system/`
- Artifacts found:
  - `lucid_mcp_server.py`
  - `scripts/mcp_http_fallback_server.py`
  - `packages/mcp_server/server.py`
  - `daemon_rag_system/daemon_rag_mcp_server.py`
  - `context_capsule_wire_and_mapper_v1/daemon/lucid_mcp_server.py`

### Pass B - Related concept search
- Queries used: `tools/list`, `mcp/list`, `mcp/execute`, `json-rpc`, `transport smoke`, `tool parity`
- Locations searched: `lucid_mcp_server.py`, `scripts/`, `docs/`, `packages/lucid_mcp_server/`, `packages/mcp_server/`
- Artifacts found:
  - `lucid_mcp_server.py` handlers for `tools/list` and tool dispatch
  - `scripts/check_mcp_tool_parity.py`
  - `scripts/mcp_transport_smoke.py`
  - `packages/mcp_server/server.py` with `/mcp/tools/list`

### Pass C - Structural search
- Queries used: `mcp_control`, `run_mcp_http_fallback`, `run_mcp_dev`, `verify_mcp_tools`
- Locations searched: `scripts/`, `scripts/launchers/`, `packages/lucid_mcp_server/`, `packages/mcp_rag_proxy/`
- Artifacts found:
  - `scripts/mcp_control.ps1`
  - `scripts/run_mcp_http_fallback.ps1`
  - `scripts/run_mcp_dev.ps1`, `scripts/run_mcp_dev.bat`
  - `scripts/verify_mcp_tools.py`
  - `packages/mcp_rag_proxy/*`

### Pass D - Drift/duplicate search
- Queries used: `run_mcp_`, `test_mcp_`, `minimal_mcp`, `archive mcp`, `snapshot mcp`
- Locations searched: `archive/`, `snapshots/`, `context_capsule_wire_and_mapper_v1/daemon/`
- Artifacts found:
  - many archived startup/test variants (`archive/run_mcp_*.py`, `archive/test_mcp_*.py`)
  - snapshot backup (`snapshots/run_mcp_32_tools_backup_2025-10-28.py`)
  - daemon copy of `lucid_mcp_server.py` in context capsule tree
- Artifacts rejected:
  - `archive/*` and `snapshots/*` MCP scripts rejected as non-canonical runtime history
  - context-capsule daemon copy rejected as duplicate copy path

### Variant comparison

| Variant | Path | Type | Completeness | Recency | Architectural fidelity | Supersedes? | Decision |
|---|---|---|---|---|---|---|---|
| A | `lucid_mcp_server.py` | code | full monolith tool surface | commit `ace529da3` (2026-03-03) | highest for active MCP tooling | no explicit supersedes marker | CANONICAL (primary MCP implementation) |
| B | `scripts/mcp_http_fallback_server.py` | code | full HTTP bridge to monolith | commit `e35926122` (2026-03-03) | high (active transport path on :5001) | additive bridge | CANONICAL (runtime bridge) |
| C | `packages/mcp_server/server.py` | code | FastAPI MCP server with own stack | commit `b391dee9e` (2025-10-23) | medium (alternate architecture) | no | ALTERNATE/LEGACY |
| D | `daemon_rag_system/daemon_rag_mcp_server.py` | code | RAG-focused MCP daemon | commit `894d317a4` (2025-11-04) | medium (specialized) | no | SPECIALIZED ALTERNATE |
| E | `context_capsule_wire_and_mapper_v1/daemon/lucid_mcp_server.py` | code | near-copy of monolith | local mtime 2026-03-01 | low (duplicate path) | no | DUPLICATE |

Canonical decision:
- MCP runtime canon is `lucid_mcp_server.py` + `scripts/mcp_http_fallback_server.py`.
- Tool parity is currently proven at 103/103 via `scripts/check_mcp_tool_parity.py`.

Remaining uncertainty:
- Whether `packages/mcp_server/server.py` should be retired or retained as supported alternate path is not explicitly adjudicated.

---

## 2) JOC / Joint Operations Center

### Pass A - Direct name search
- Search target: primary JOC implementation
- Queries used: `joc`, `JOC`, `Joint Operations`, `OPUS1_JOC`
- Locations searched: `packages/`, `docs/`, `ide_orchestration/prototypes/`
- Artifacts found:
  - `packages/joc/`
  - `docs/OPUS1_JOC_*`
  - `docs/JOC_MASTER_PLAN.md`, `docs/CANON_JOC_UI_ARCHITECTURE.md`

### Pass B - Related concept search
- Queries used: `DispatchPage`, `SessionPage`, `Oracle`, `MissionBuilder`, `AgentComms`
- Locations searched: `packages/joc/src/pages/`, `packages/joc/src/services/`, docs
- Artifacts found:
  - full page set in `packages/joc/src/pages/`
  - orchestration/service files in `packages/joc/src/services/`
  - canon UI architecture doc

### Pass C - Structural search
- Queries used: `package.json`, `plans/`, `bas-e2e-smoke`, `src/App.tsx`
- Locations searched: `packages/joc/`
- Artifacts found:
  - `packages/joc/package.json`
  - `packages/joc/plans/*`
  - `packages/joc/scripts/bas-e2e-smoke.mjs`
  - `packages/joc/src/App.tsx`

### Pass D - Drift/duplicate search
- Queries used: `ide_chat_app`, `dac prototype`, `JOC doc variants`
- Locations searched: `packages/ide_chat_app/`, `ide_orchestration/prototypes/dac/`, `docs/`
- Artifacts found:
  - `packages/ide_chat_app/` (parallel app surface)
  - extensive DAC prototype tree with coordination docs
  - multiple JOC strategy docs
- Artifacts rejected:
  - DAC prototype tree rejected as historical/prototype source for current JOC runtime
  - `packages/ide_chat_app` rejected as non-JOC runtime for this system (kept as alternate app, not JOC canon)

### Variant comparison

| Variant | Path | Type | Completeness | Recency | Architectural fidelity | Supersedes? | Decision |
|---|---|---|---|---|---|---|---|
| A | `packages/joc/` | code | high; full app shell and service wiring | local mtime active (2026-03-04) | highest for JOC runtime | no explicit marker | CANONICAL |
| B | `packages/ide_chat_app/` | code | substantial but different app track | active but separate | medium for JOC goals | no | SEPARATE APP SURFACE |
| C | `ide_orchestration/prototypes/dac/` | code+docs | prototype-rich, not production target | older/historical mix | low for current runtime | no | HISTORICAL PROTOTYPE |
| D | `docs/CANON_JOC_UI_ARCHITECTURE.md` | doc | architecture policy | 2026-03-03 | high as design canon | no | CANONICAL DOC (policy) |

Canonical decision:
- JOC code canon is `packages/joc/`.

Remaining uncertainty:
- `packages/ide_chat_app` remains a live alternate surface and appears in legacy launchers; separation boundaries are documented but not fully deconflicted across all scripts.

---
## 3) Context Systems / Context Mapper

### Pass A - Direct name search
- Search target: context mapper and context system implementations
- Queries used: `context_mapper`, `context_capsule`, `context_bootloader`, `timeline_context_system`, `ContextAttachment`
- Locations searched: `IDE/src-tauri/`, `context_capsule_wire_and_mapper_v1/`, `packages/`, `docs/`
- Artifacts found:
  - `IDE/src-tauri/src/context_mapper/*`
  - `IDE/src-tauri/src/context_service.rs`
  - `context_capsule_wire_and_mapper_v1/context_mapper_lab/*`
  - `packages/context_bootloader/*`
  - `packages/timeline_context_system/*`

### Pass B - Related concept search
- Queries used: `shadow_sync`, `mapper_adapter`, `prompt_context_tracker`, `dual_prompt`, `phase2b_context_packet`
- Locations searched: context capsule tree, timeline context package, docs
- Artifacts found:
  - `context_capsule_wire_and_mapper_v1/shadow_sync/*`
  - `context_capsule_wire_and_mapper_v1/shadow_sync/mapper_adapter_v0_1.py`
  - `packages/timeline_context_system/prompt_context_tracker.py`
  - `docs/phase2b_context_packet/*`

### Pass C - Structural search
- Queries used: `context_service`, `context_mapper/mod.rs`, `smart_context_loader.py`, package manifests
- Locations searched: `IDE/src-tauri/`, `packages/context_bootloader/`, `packages/timeline_context_system/`, docs packet manifests
- Artifacts found:
  - live Rust mapper module structure in `IDE/src-tauri/src/context_mapper/`
  - `packages/context_bootloader/smart_context_loader.py`
  - timeline context system package tree
  - packet snapshots in `docs/phase2b_context_packet/`

### Pass D - Drift/duplicate search
- Queries used: `TAGGED`, `TAGGED_TAGGED`, `out/live_mapper_snapshot`, duplicate mapper roots
- Locations searched: `packages/timeline_context_system/`, context capsule output dirs, docs packet copies
- Artifacts found:
  - large duplicate set in timeline package (`*_TAGGED.py`, `*_TAGGED_TAGGED.py`)
  - archived output snapshots in `context_capsule_wire_and_mapper_v1/shadow_sync/out/`
  - packet copies of mapper sources under docs
- Artifacts rejected:
  - `target/` and generated outputs rejected as non-canonical implementation sources
  - `*_TAGGED*` duplicates rejected as duplicate variants unless explicitly re-promoted

### Variant comparison

| Variant | Path | Type | Completeness | Recency | Architectural fidelity | Supersedes? | Decision |
|---|---|---|---|---|---|---|---|
| A | `IDE/src-tauri/src/context_mapper/*` + `context_service.rs` | code | substantial live seam implementation | mtime 2026-03-01 | high for lane-A live seam | no explicit supersedes | PRIMARY LIVE-SEAM CANDIDATE |
| B | `context_capsule_wire_and_mapper_v1/` | code+docs | strong prototype package (lab, shadow sync, wire proof) | mtime 2026-03-01 | high for lane-B shadow/prototype | no | SHADOW/PROTOTYPE CANDIDATE |
| C | `packages/context_bootloader/` | code | focused loader/tooling | tracked older baseline | medium; support layer | no | SUPPORTING CONTEXT LAYER |
| D | `packages/timeline_context_system/` | code | broad feature set but many duplicate variants | mixed | medium; noisy from duplicate copies | no | PART-BUILT / NEEDS DEDUPE |
| E | `docs/phase2b_context_packet/*` | doc+code snapshot | packetized copy set | mtime 2026-03-04 | low as runtime source; high as evidence | no | EVIDENCE SNAPSHOT |

Canonical decision:
- No single global context canon is safely claimable yet.
- Lane-specific likely canon: live seam in `IDE/src-tauri/src/context_mapper/*`; shadow/prototype in `context_capsule_wire_and_mapper_v1/*`.

Remaining uncertainty:
- STATUS: UNCERTAIN - MULTIPLE COMPETING SOURCES.
- Explicit promotion criteria between context mapper families is not yet codified in one decisive runtime contract.

---

## 4) Memory Systems

### Pass A - Direct name search
- Search target: persistent memory and retrieval systems
- Queries used: `cmc_service`, `hhni`, `mcp_memory`, `mcp_ai_messages`, `memory_store`, `retrieval`
- Locations searched: `packages/cmc_service/`, `packages/hhni/`, repo root memory files
- Artifacts found:
  - `packages/cmc_service/*`
  - `packages/hhni/*`
  - `mcp_memory/`
  - `mcp_ai_messages.json`
  - `codex_workspace/persistence/collaboration/codex_ai_messages.json`

### Pass B - Related concept search
- Queries used: `bitemporal`, `get_memory_stats`, `semantic search`, `index_available`, `retriever_available`
- Locations searched: MCP runtime output, CMC/HHNI files, docs
- Artifacts found:
  - live `get_memory_stats` response from MCP fallback
  - CMC tests for governance/policy integration
  - HHNI retrieval/index modules

### Pass C - Structural search
- Queries used: `memory_store.py`, `retrieval.py`, tests, index/tag files
- Locations searched: CMC, HHNI, `mcp_memory/index/tags/`
- Artifacts found:
  - `packages/cmc_service/memory_store.py`
  - `packages/hhni/retrieval.py`
  - broad CMC/HHNI test surfaces
  - persisted tag indexes in `mcp_memory/index/tags/*.json`

### Pass D - Drift/duplicate search
- Queries used: `*_TAGGED.py`, duplicate memory managers, archive memory docs
- Locations searched: CMC, HHNI, cursor-addon, archive/docs
- Artifacts found:
  - many `*_TAGGED.py` duplicates in CMC/HHNI
  - `cursor-addon/src/memory/memoryManager.ts` (separate client-side memory utility)
- Artifacts rejected:
  - `*_TAGGED.py` copies rejected as duplicate variants unless explicitly active
  - cursor-addon memory manager rejected as canonical AIM-OS memory backend

### Variant comparison

| Variant | Path | Type | Completeness | Recency | Architectural fidelity | Supersedes? | Decision |
|---|---|---|---|---|---|---|---|
| A | `packages/cmc_service/` | code | high | commit on key file `1d46acabd` (2026-02-19) | highest for memory persistence | no | CANONICAL MEMORY STORE |
| B | `packages/hhni/` | code | high module coverage | `retrieval.py` commit `93dd414a4` (2025-12-02) | high for retrieval | no | CANONICAL RETRIEVAL LAYER (partially wired live) |
| C | `mcp_memory/` | data runtime store | operational data present | active runtime writes | high as active persistence surface | no | CANONICAL RUNTIME DATA SURFACE |
| D | `mcp_ai_messages.json` (+ codex workspace mirror) | data | active collaboration persistence | active | medium/high for message lane | no | CANONICAL MESSAGE DATA SURFACE |
| E | `cursor-addon/src/memory/memoryManager.ts` | code | app-local | active addon track | low for AIM-OS backend memory canon | no | LOCAL CLIENT MEMORY ONLY |

Canonical decision:
- CMC + HHNI + `mcp_memory/` + message stores are canonical memory stack components.

Remaining uncertainty:
- Live MCP stats currently report HHNI index/retriever unavailable; wiring/initialization state remains partially degraded at runtime.

---
## 5) Orchestration / Agent Coordination

### Pass A - Direct name search
- Search target: agent messaging and coordination control paths
- Queries used: `.agent/comms`, `send_ai_message`, `get_ai_messages`, `roundtable`, `offline_comms`
- Locations searched: `.agent/`, `scripts/`, `docs/`, `lucid_mcp_server.py`
- Artifacts found:
  - `.agent/comms/*`
  - `scripts/agent_comms/*`
  - `scripts/offline_comms/*`
  - MCP collaboration tools in `lucid_mcp_server.py`

### Pass B - Related concept search
- Queries used: `holder_id`, `identity lock`, `comms_cli`, `bootstrap_agent_session`, `runtime_action_lock`
- Locations searched: scripts + protocol docs
- Artifacts found:
  - `scripts/agent_comms/comms_cli.py`
  - `scripts/agent_comms/identity_session_lock.py`
  - `scripts/offline_comms/runtime_action_lock.py`

### Pass C - Structural search
- Queries used: `COMMS_PROTOCOL`, `COMMS_CANONICAL`, `START_HERE`, thread index
- Locations searched: `.agent/comms/`, `docs/roundtable/`, `docs/communications_mcp_down/`
- Artifacts found:
  - `.agent/comms/COMMS_PROTOCOL.md`
  - `.agent/comms/COMMS_CANONICAL.md`
  - `docs/roundtable/START_HERE.md`
  - thread/index files in `docs/communications_mcp_down/threads/`

### Pass D - Drift/duplicate search
- Queries used: duplicate thread channels, overlapping protocol docs
- Locations searched: `.agent/comms/`, `docs/roundtable/`, `docs/communications_mcp_down/`
- Artifacts found:
  - three intentional channels (MCP tools, `.agent/comms`, roundtable files)
- Artifacts rejected:
  - none rejected as obsolete by default because layered fallback is intentional and documented

### Variant comparison

| Variant | Path | Type | Completeness | Recency | Architectural fidelity | Supersedes? | Decision |
|---|---|---|---|---|---|---|---|
| A | MCP tools in `lucid_mcp_server.py` (`send_ai_message`, `get_ai_messages`) | code | high | active in monolith | high for MCP-up mode | no | CANONICAL WHEN MCP UP |
| B | `.agent/comms/*` + `scripts/agent_comms/*` | file protocol + CLI | high | active (2026-03-04 updates) | high for local deterministic collaboration | no | CANONICAL SUPPORT PATH |
| C | `docs/roundtable/*` + `scripts/offline_comms/*` | doc+scripts | high | active (2026-03-04/05) | high for MCP-down mode | no | CANONICAL MCP-DOWN PATH |

Canonical decision:
- Coordination canon is layered, not singular:
  - MCP collaboration tools when available
  - offline/roundtable + `.agent/comms` fallback when MCP unstable

Remaining uncertainty:
- Operational priority order between `.agent/comms` and roundtable posting is documented but still prone to human/agent drift under incident pressure.

---

## 6) Browser/Chat Integration

### Pass A - Direct name search
- Search target: ChatGPT/Gemini browser execution path
- Queries used: `browser-automation-service`, `mcpBridge`, `DispatchPage`, `SessionPage`, `chatgpt`, `gemini`
- Locations searched: `packages/browser-automation-service/`, `packages/joc/`, docs
- Artifacts found:
  - BAS service and bridge endpoints
  - JOC pages and BAS client
  - provider scripts (`chatgpt-login.json`, `gemini-login.json`)

### Pass B - Related concept search
- Queries used: `providerSelectors`, `auth gate`, `credential vault`, `start-new-chat`, `extract-response`
- Locations searched: BAS API/service files + shared selector registry
- Artifacts found:
  - `packages/browser-automation-service/src/api/mcpBridge.ts`
  - `packages/shared/providerSelectors.ts`
  - vault integration in BAS connection routes

### Pass C - Structural search
- Queries used: `:5002`, `basClient`, `sessionStore`, `missionOrchestrator`, smoke scripts
- Locations searched: `packages/joc/src/services/`, `packages/joc/src/store/`, `packages/joc/scripts/`
- Artifacts found:
  - `packages/joc/src/services/basClient.ts`
  - `packages/joc/src/store/sessionStore.ts`
  - `packages/joc/src/pages/DispatchPage.tsx`
  - `packages/joc/scripts/bas-e2e-smoke.mjs`

### Pass D - Drift/duplicate search
- Queries used: `BrowserAutomationPanel`, `DAC`, alternate browser panels, seam findings
- Locations searched: `ide_orchestration/prototypes/dac/`, `packages/ide_chat_app/`, docs audits
- Artifacts found:
  - DAC browser panel prototypes
  - alternate browser UI in `packages/ide_chat_app/`
  - active seam findings in `docs/Composer/FINDINGS_MASTER_LIST.md` (#10, #11)
- Artifacts rejected:
  - DAC browser panel path rejected as canonical runtime integration path

### Variant comparison

| Variant | Path | Type | Completeness | Recency | Architectural fidelity | Supersedes? | Decision |
|---|---|---|---|---|---|---|---|
| A | `packages/browser-automation-service/` | code | high; API + tests + runbook | active (mtime 2026-03-04) | highest for browser automation backend | no | CANONICAL BACKEND |
| B | `packages/joc/src/services/basClient.ts` + `sessionStore.ts` | code | high, actively wired | active | high for UI integration | no | CANONICAL JOC INTEGRATION LAYER |
| C | `packages/joc/src/pages/DispatchPage.tsx` | code | functional but known seam defects | active | medium (known browserId/store issues) | no | PART-BUILT / NEEDS HARDENING |
| D | `ide_orchestration/prototypes/dac/src/panels/*` | code | prototype | historical | low for current runtime | no | HISTORICAL PROTOTYPE |
| E | `packages/ide_chat_app/src/components/BrowserWindow.tsx` | code | alternate app surface | active | medium for alt app; not JOC canon | no | ALTERNATE APP PATH |

Canonical decision:
- Browser/chat integration canon is `JOC -> BAS`.

Remaining uncertainty:
- JOC dispatch/session seam remains unresolved in current source evidence (`DispatchPage` still uses `t.session.id` pattern flagged in findings #10/#11).

---
## 7) Tool Registries

### Pass A - Direct name search
- Search target: authoritative tool lists and registration points
- Queries used: `tools/list`, `check_mcp_tool_parity`, `verify_mcp_tools`, `cursor_commands`, `tools_metadata`
- Locations searched: monolith, scripts, packages
- Artifacts found:
  - `lucid_mcp_server.py` tool list and call handlers
  - `scripts/check_mcp_tool_parity.py`
  - `scripts/verify_mcp_tools.py`
  - `packages/lucid_mcp_server/tools/cursor_commands.py`
  - `packages/mcp_rag_proxy/tools_metadata.json`

### Pass B - Related concept search
- Queries used: `register`, `tool analyzer`, `api_service_registry`, `registry`
- Locations searched: `packages/lucid_mcp_server/`, `packages/api_service_registry/`, `packages/mcp_rag_proxy/`, docs
- Artifacts found:
  - `register_cursor_commands_tools` in cursor commands module
  - `packages/api_service_registry/llm/api_service_registry.py`
  - `packages/mcp_rag_proxy/tool_analyzer.py`

### Pass C - Structural search
- Queries used: source-of-truth detector, parity scripts, architecture overview
- Locations searched: `scripts/`, `docs/`
- Artifacts found:
  - `scripts/detect_source_of_truth.py` (extracts listed vs callable tool surfaces)
  - `docs/ARCHITECTURE_OVERVIEW.md` note about tool count (stale)

### Pass D - Drift/duplicate search
- Queries used: stale tool count claims, legacy tool specification docs
- Locations searched: docs
- Artifacts found:
  - `docs/ARCHITECTURE_OVERVIEW.md` says 93 tools (stale)
  - `docs/cross_model/MCP_TOOL_SPECIFICATIONS.md` from 2025 proposal era
- Artifacts rejected:
  - stale numeric count claims in older docs rejected as canonical runtime truth

### Variant comparison

| Variant | Path | Type | Completeness | Recency | Architectural fidelity | Supersedes? | Decision |
|---|---|---|---|---|---|---|---|
| A | `lucid_mcp_server.py` + `scripts/check_mcp_tool_parity.py` | code | full with parity checks | active | highest for runtime tools | no | CANONICAL TOOL REGISTRY |
| B | `packages/mcp_server/server.py` (`/mcp/tools/list`) | code | limited alternate API | older (2025-10-23) | medium alternate path | no | ALTERNATE/LEGACY |
| C | `packages/lucid_mcp_server/tools/cursor_commands.py` | code | focused tool family | active module | additive to MCP ecosystem | no | INTEGRATED SUB-REGISTRY |
| D | `packages/api_service_registry/llm/api_service_registry.py` | code | provider API registry | active module | adjacent registry, not MCP `tools/list` authority | no | RELATED BUT NOT CANONICAL MCP LIST |
| E | `packages/mcp_rag_proxy/tools_metadata.json` | data | metadata only | present | low as authoritative runtime list | no | SUPPORTING METADATA |

Canonical decision:
- Authoritative tool canon is monolith `tools/list`/`tools/call` parity (currently 103 tools).

Remaining uncertainty:
- none material for current runtime registry authority.

---

## 8) Launch / Runtime Bridges

### Pass A - Direct name search
- Search target: startup and bridge entrypoints for active runtime surfaces
- Queries used: `mcp_control`, `run_mcp_http_fallback`, `START_BAS_DETERMINISTIC`, `LAUNCH_HYBRID_SOLUTION`, `daemon_bridge`
- Locations searched: `scripts/`, `scripts/launchers/`, `IDE/src-tauri/`, docs
- Artifacts found:
  - `scripts/mcp_control.ps1`
  - `scripts/run_mcp_http_fallback.ps1`
  - `scripts/launchers/START_BAS_DETERMINISTIC.ps1`
  - `scripts/launchers/LAUNCH_HYBRID_SOLUTION.ps1`
  - `IDE/src-tauri/src/daemon_bridge.rs`

### Pass B - Related concept search
- Queries used: `health`, `port 5001`, `port 5002`, `fallback`, `bridge`
- Locations searched: launcher scripts + runbooks
- Artifacts found:
  - health-gated start/stop/test logic in `mcp_control.ps1`
  - fallback startup wrapper in `run_mcp_http_fallback.ps1`
  - deterministic BAS launcher with stale listener recycle logic

### Pass C - Structural search
- Queries used: launcher canon docs, operational runbooks, startup guides
- Locations searched: docs + scripts
- Artifacts found:
  - `docs/OPUS1_BROWSER_SYSTEM_RUNBOOK_V1.md`
  - `apps/LAUNCHER_CANON.md` (broad launcher inventory)

### Pass D - Drift/duplicate search
- Queries used: `launch` across `apps/` and examples
- Locations searched: `apps/`
- Artifacts found:
  - many launch scripts for unrelated app examples
- Artifacts rejected:
  - non-AIMOS-core app launchers rejected as runtime canon for MCP/JOC/BAS operational spine

### Variant comparison

| Variant | Path | Type | Completeness | Recency | Architectural fidelity | Supersedes? | Decision |
|---|---|---|---|---|---|---|---|
| A | `scripts/mcp_control.ps1` | script | full lifecycle (status/start/stop/test) | active | highest for MCP runtime control | no | CANONICAL MCP CONTROL |
| B | `scripts/run_mcp_http_fallback.ps1` | script | focused fallback launcher | active | high; supports canonical bridge | additive | CANONICAL MCP START WRAPPER |
| C | `scripts/launchers/START_BAS_DETERMINISTIC.ps1` | script | deterministic BAS startup and health gate | active | high for BAS runtime | no | CANONICAL BAS LAUNCHER |
| D | `scripts/launchers/LAUNCH_HYBRID_SOLUTION.ps1` | script | hybrid/legacy launcher for ide_chat_app stack | active but alternate | medium for current JOC spine | no | ALTERNATE LEGACY LAUNCHER |
| E | `IDE/src-tauri/src/daemon_bridge.rs` | code bridge | bridge seam implementation | active code | high for IDE runtime bridge seam | no | CANONICAL BRIDGE COMPONENT |

Canonical decision:
- Operational launch canon for current spine: `mcp_control.ps1` + `run_mcp_http_fallback.ps1` + `START_BAS_DETERMINISTIC.ps1` (+ JOC package scripts).

Remaining uncertainty:
- multiple historical launchers remain and can still cause operator confusion without explicit deprecation labels.

---
## 9) Agent Protocol / Genome / Packet Systems

### Pass A - Direct name search
- Search target: agent identity, cloning, and packet specs
- Queries used: `genome`, `GENOME_PROTOCOL`, `AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC`, `packet`, `handoff`
- Locations searched: `.agent/`, `docs/`, `knowledge_architecture/`
- Artifacts found:
  - `.agent/genomes/*.genome.md`
  - `.agent/genomes/GENOME_PROTOCOL.md`
  - `docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V2.md`
  - `docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V3.md`
  - multiple thread/handoff packets

### Pass B - Related concept search
- Queries used: `fission`, `lineage`, `specialist`, `identity continuity protocol`
- Locations searched: docs + knowledge architecture + packages
- Artifacts found:
  - V3 spec with fission and lineage model
  - identity continuity protocol in `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
  - specialist runtime in `packages/specialist_system/*`

### Pass C - Structural search
- Queries used: `systems/agent_genome`, `T0/T1/T2/T3/T4`, `bootstrap_agent_session`
- Locations searched: `knowledge_architecture/systems/agent_genome/`, `scripts/agent_comms/`
- Artifacts found:
  - full agent_genome documentation hierarchy in knowledge architecture
  - bootstrap/identity tooling scripts in `scripts/agent_comms/`

### Pass D - Drift/duplicate search
- Queries used: `V2`, `V3`, supersedes markers, packet duplicates
- Locations searched: docs
- Artifacts found:
  - V3 explicitly says it supersedes V2
  - many dated thread packets and handoff packets
- Artifacts rejected:
  - V2 rejected as superseded by V3 for forward design intent
  - older thread packets rejected as canonical definitions unless referenced by active decision log

### Variant comparison

| Variant | Path | Type | Completeness | Recency | Architectural fidelity | Supersedes? | Decision |
|---|---|---|---|---|---|---|---|
| A | `.agent/genomes/*` + `GENOME_PROTOCOL.md` | runtime identity docs | high for operational identity loading | active (2026-03-04 updates) | high for current practice | no | CANONICAL OPERATIONAL IDENTITY SYSTEM |
| B | `docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V3.md` | design spec | high proposal depth | 2026-03-04 | high as latest design intent | supersedes V2 | CANONICAL DESIGN REFERENCE |
| C | `docs/AGENT_BUILDING_AND_CLONING_SYSTEM_SPEC_V2.md` | design spec | still useful for lineage/context | 2026-03-04 | medium; older than V3 | superseded by V3 | HISTORICAL/SUPERSEDED |
| D | `knowledge_architecture/systems/agent_genome/*` | architecture docs | high | older but complete | high conceptual architecture | no | CANONICAL ARCHITECTURE REFERENCE |
| E | `packages/specialist_system/*` | runtime code | implemented | active package | high for current specialization runtime | no | CANONICAL RUNTIME COMPONENT |

Canonical decision:
- Operational canon today is `.agent/genomes` + comms/bootstrap scripts + `packages/specialist_system` runtime.
- Design canon for future extension is V3 spec.

Remaining uncertainty:
- runtime `packages/agent_genome/` implementation is still not present as a distinct production package; architecture remains split across docs and adjacent runtime components.

---

## 10) Governance Systems

### Pass A - Direct name search
- Search target: active governance and authority documents
- Queries used: `IDENTITY_CANON`, `DECISION_LOG`, `WRITE_POLICY`, `ROLE_CONTINUITY_CANON`, `ROLE_CONTINUITY_STATE`
- Locations searched: `docs/roundtable/`, `docs/communications_mcp_down/`, `docs/agents/`, top-level docs
- Artifacts found:
  - `docs/roundtable/IDENTITY_CANON.md`
  - `docs/roundtable/decisions/DECISION_LOG.md`
  - `docs/communications_mcp_down/WRITE_POLICY.md`
  - `docs/agents/ROLE_CONTINUITY_CANON.md`
  - `docs/ROLE_CONTINUITY_STATE.md`

### Pass B - Related concept search
- Queries used: `incident`, `recovery protocol`, `code freeze`, `roundtable start`, `index`
- Locations searched: roundtable and comms-down docs
- Artifacts found:
  - `docs/roundtable/START_HERE.md`
  - `docs/roundtable/INDEX.md`
  - recovery protocol docs in `docs/communications_mcp_down/agents/`
  - incident/audit documents

### Pass C - Structural search
- Queries used: governance doctrine roots, canon read order, decision templates
- Locations searched: `docs/AIM_OS_PRIME_*`, `docs/roundtable/templates/`, comms templates
- Artifacts found:
  - `docs/AIM_OS_PRIME_CANON_INDEX_V1.md`
  - roundtable decision templates

### Pass D - Drift/duplicate search
- Queries used: conflicting role maps, duplicate governance packets
- Locations searched: roundtable docs vs role continuity docs vs recovery packets
- Artifacts found:
  - conflict exists between later `docs/roundtable/IDENTITY_CANON.md` and earlier `docs/agents/ROLE_CONTINUITY_CANON.md`
  - multiple governance packets with overlapping role claims
- Artifacts rejected:
  - earlier role map docs rejected as current governance canon due later mandatory roundtable identity canon + decision log governance path

### Variant comparison

| Variant | Path | Type | Completeness | Recency | Architectural fidelity | Supersedes? | Decision |
|---|---|---|---|---|---|---|---|
| A | `docs/roundtable/IDENTITY_CANON.md` | governance doc | high | mtime 2026-03-04 19:17 | highest for current roundtable mode (explicit mandatory language) | implicit precedence by recency + START_HERE | CANONICAL IDENTITY/LANE MAP |
| B | `docs/agents/ROLE_CONTINUITY_CANON.md` | governance doc | high | mtime 2026-03-04 12:21 | medium; earlier crisis-mode map | no explicit supersedes note | HISTORICAL/CONFLICTING |
| C | `docs/ROLE_CONTINUITY_STATE.md` | status snapshot | medium | mtime 2026-03-04 12:29 | low as evergreen canon | no | HISTORICAL SNAPSHOT |
| D | `docs/communications_mcp_down/WRITE_POLICY.md` | governance policy | high | active | high for thread integrity | no | CANONICAL WRITE POLICY |
| E | `docs/roundtable/decisions/DECISION_LOG.md` | governance log | high | active (DEC-006 present) | high for adjudication history | no | CANONICAL DECISION RECORD |
| F | `docs/AIM_OS_PRIME_CANON_INDEX_V1.md` | doctrine index | high | 2026-03-02 | high for architecture read order | no | CANONICAL PROGRAM DOCTRINE |

Canonical decision:
- Governance canon for current operations is:
  - `docs/roundtable/IDENTITY_CANON.md`
  - `docs/roundtable/decisions/DECISION_LOG.md`
  - `docs/communications_mcp_down/WRITE_POLICY.md`
  - `docs/roundtable/START_HERE.md` and `docs/roundtable/INDEX.md`

Remaining uncertainty:
- STATUS: UNCERTAIN - COMPETING HISTORICAL ROLE MAPS remain in-tree without explicit deprecation headers on older files.

---

## Cross-System Rejected Artifacts Ledger

| Artifact class | Rejected examples | Why rejected |
|---|---|---|
| Archive MCP scripts | `archive/run_mcp_*.py`, `archive/test_mcp_*.py` | historical diagnostics, not active runtime canon |
| Snapshot backups | `snapshots/run_mcp_32_tools_backup_2025-10-28.py` | backup artifact, not current entrypoint |
| Build outputs | `**/target/**`, `**/out/**`, `**/dist/**` | generated artifacts, not source of truth |
| Duplicate tagged files | `*_TAGGED.py`, `*_TAGGED_TAGGED.py` in context/timeline/memory packages | duplicate variant noise without explicit active promotion |
| Prototype UI tracks | `ide_orchestration/prototypes/dac/*` browser/JOC paths | historical prototypes, not current operational spine |
| Non-core app launchers | many `apps/**/LAUNCH*` scripts | unrelated to active MCP/JOC/BAS operational path |

---

## Open Uncertainty Register

1. MCP alternate server adjudication
- `packages/mcp_server/server.py` still exists as a viable alternate and can confuse startup/operator behavior.

2. Context system consolidation
- Multiple strong candidates exist (`IDE/src-tauri/context_mapper`, context capsule stack, context bootloader, timeline context system).
- Requires explicit consolidation decision and promotion contract.

3. JOC browser seam
- Findings #10/#11 still point to dispatch/session source-of-truth mismatch risk in current JOC source.

4. Governance map conflict cleanup
- Older role continuity docs conflict with newer roundtable identity canon and need explicit deprecation markers.

5. Launcher surface overload
- Many legacy launchers remain discoverable; without deprecation tags operators can invoke wrong runtime path.

---

## Completion Check Against Addendum

All required systems were processed with A/B/C/D passes:
- MCP server(s)
- JOC
- context systems/context mapper
- memory systems
- orchestration/agent coordination
- browser/chat integration
- tool registries
- launch/runtime bridges
- agent protocol/genome/packet systems
- governance systems

Evidence includes competing variants, canon decisions, rejected artifacts, and explicit uncertainty where needed.
