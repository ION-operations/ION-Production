# AIM-OS Master System Index

**Type:** Full manual audit — guaranteed hierarchical index  
**Date:** 2026-03-09  
**Author:** Ledger (agent)  
**Status:** Authoritative — no stone unturned  
**Sources:** Repo crawl, PROJECT_TRUTH, AIMOS_MAJOR_SYSTEMS, 00_MASTER_AIMOS_SYSTEM_MAP, package READMEs, package.json

---

## How to Use

- **Priority order:** Tier 1 (domains) → Tier 2 (systems) → Tier 3 (subsystems). Most important branches first.
- **Cross-reference:** `.agent/SYSTEM_REGISTRY.md` for machine-generated registry; this document for curated, audited truth.
- **Canonical paths:** All paths relative to repo root unless noted.

---

## Tier 1: Domains (Priority Order)

| # | Domain | Purpose | Systems Count |
|---|--------|---------|---------------|
| 1 | Core Infrastructure | Memory, retrieval, provenance, orchestration, evidence, quality | 9 |
| 2 | AI Engine | Pipeline, agents, swarm, providers, safety, learning | 28+ |
| 3 | Context System | Mapping, concierge, pack building, large files | 6 |
| 4 | Agent System | Genomes, runtime, spawner, mesh, roundtable | 8 |
| 5 | MCP & Transport | Lucid MCP, HTTP bridge, RAG proxy, daemon | 6 |
| 6 | UI & Cockpit | JOC, IDE chat, mobile, tournament | 6 |
| 7 | Consciousness & Safety | CAS, SCOR, IIS, consciousness engines | 12 |
| 8 | Supporting Packages | Router, prompts, schemas, integration | 25+ |
| 9 | Apps | Echo Forge Loop, ProEarth, system-atlas | 15+ |
| 10 | Scripts & Utilities | Launchers, MCP control, sentinel, agent comms | 50+ |
| 11 | Documentation | Knowledge architecture, SAM, SUPER_INDEX | 5 |
| 12 | Root-Level Systems | daemon_rag_system, ide_orchestration, cursor-addon | 8 |

---

## Tier 2 & 3: Systems by Domain

### 1. Core Infrastructure (9 systems)

| System | Path | Purpose | Subsystems |
|--------|------|---------|------------|
| **CMC** (Context Memory Core) | `packages/cmc_service/` | Bitemporal memory substrate — atoms, snapshots, provenance | memory_store, models, repository, store_io, advanced_compression |
| **HHNI** (Hierarchical Hypergraph Neural Index) | `packages/hhni/` | Physics-guided retrieval, DVNS, fractal indexing | budget_manager, retrieval, dvns_physics, deduplication, conflict_resolver, compressor |
| **VIF** (Verifiable Intelligence Framework) | `packages/vif/` | Provenance, κ-gating, confidence calibration | witness, confidence_tracker, kappa_gate, ece_tracker, audit_api |
| **APOE** (AI-Powered Orchestration Engine) | `packages/apoe/` | Execution planning, ACL compilation, quality gates | acl_parser, plix_compiler, execution_orchestrator, roles |
| **SEG** (Shared Evidence Graph) | `packages/seg/` | Knowledge synthesis, contradiction detection, evidence graph | graph operations, evidence ingestion, synthesis |
| **SDF-CVF** (Atomic Evolution Framework) | `packages/sdfcvf/` | Quartet invariant, parity enforcement, DORA metrics | quartet detection, parity calculation, blast_radius, gate system |
| **TCS** (Timeline Context System) | `packages/timeline_context_system/` | Temporal consciousness, session continuity | adaptive_context_dumping, timeline entries, context management |
| **CAS** (Cognitive Analysis System) | `packages/cas/` | Meta-cognitive monitoring, failure mode analysis | activation, attention, failure_mode_analysis |
| **IIS** (Intuitive Intelligence System) | `packages/intuitive_intelligence_system/` | 4D reasoning, emotional salience, pattern matching | compute_intuition, update_intuition_weights |

---

### 2. AI Engine (28+ systems)

| System | Path | Purpose |
|--------|------|---------|
| **AIEngine** | `scripts/ai_engine/engine.py` | 7-layer pipeline: Context→Agent→Genome→VIF→LLM→Trace→Learn |
| **Chain Director** | `scripts/ai_engine/chain_director.py` | Topology-based execution, phases, quality scoring |
| **Chain Topologies** | `scripts/ai_engine/chain_topologies.py` | Phase definitions, topology results |
| **Chained Mission** | `scripts/ai_engine/chained_mission.py` | Phase chains, complexity estimation |
| **Atlas Agent** | `scripts/ai_engine/atlas_agent.py` | Project knowledge graph, module discovery |
| **System Registry** | `scripts/ai_engine/system_registry.py` | Phase 26 master index, crawl, categorize |
| **Context Mapper** | `scripts/ai_engine/context_mapper.py` | Structural index, AST extraction, FileIndex |
| **Context Concierge** | `scripts/ai_engine/context_concierge.py` | Universal context discovery |
| **Context Engine** | `scripts/ai_engine/context_engine.py` | FileInfo, chunks, editor state |
| **Context Trail** | `scripts/ai_engine/context_trail.py` | Temporal briefing, trail entries |
| **Large File Reader** | `scripts/ai_engine/large_file_reader.py` | MapReduce for files >20K chars |
| **Genome Loader** | `scripts/ai_engine/genome_loader.py` | Agent genome loading, layers |
| **Agent Runtime** | `scripts/ai_engine/agent_runtime.py` | Step execution, plan steps |
| **Agent Spawner** | `scripts/ai_engine/agent_spawner.py` | Specialist agents, SYSTEM_REGISTRY |
| **Agent Health** | `scripts/ai_engine/agent_health.py` | Provider checks, codex provider |
| **Agent Mesh** | `scripts/ai_engine/agent_mesh.py` | Rank priority, affinity graph |
| **Registry** | `scripts/ai_engine/registry.py` | Agent status, capabilities |
| **Roundtable** | `scripts/ai_engine/roundtable.py` | Multi-agent deliberation |
| **Enhanced Worker** | `scripts/ai_engine/enhanced_worker.py` | Enhanced execution |
| **LLM Router** | `scripts/ai_engine/llm_router.py` | Task routing, model selection |
| **MCP Tools** | `scripts/ai_engine/mcp_tools.py` | ai_engine_* tool wrappers |
| **Session Manager** | `scripts/ai_engine/session_manager.py` | Session state, context |
| **Docs Engine** | `scripts/ai_engine/docs_engine.py` | Package analysis, doc generation |
| **Mission Self Audit** | `scripts/ai_engine/mission_self_audit.py` | Team self-audit mission |
| **Self Improve** | `scripts/ai_engine/self_improve.py` | MCPBridge, SelfImprover |
| **Mesh Visualizer** | `scripts/ai_engine/mesh_visualizer.py` | Graph cache, visualization |
| **Agent Loop** | `scripts/ai_engine/agent_loop/` | Strategies, evolution, quality, baseline |
| **Swarm** | `scripts/ai_engine/swarm/` | Orchestrator, worker_manager, contracts |
| **Context Pack** | `scripts/ai_engine/context/` | context_pack, tool_advisor |
| **Providers** | `scripts/ai_engine/providers/` | Gemini CLI, Codex CLI, API provider |
| **Safety** | `scripts/ai_engine/safety/` | VIF gates, capability enforcement |
| **Learning** | `scripts/ai_engine/learning/` | agent_learner, outcome tracking |
| **AI Engine MCP Server** | `scripts/ai_engine/ai_engine_mcp_server.py` | 29 tools, slim MCP for Gemini CLI |

---

### 3. Context System (6 systems)

| System | Path | Purpose |
|--------|------|---------|
| **Context Mapper** | `scripts/ai_engine/context_mapper.py` | build_index, AST/TS extraction, sections, exports |
| **Context Concierge** | `scripts/ai_engine/context_concierge.py` | Atlas + ContextMapper, envelope building |
| **Context Engine** | `scripts/ai_engine/context_engine.py` | File chunks, editor state |
| **Context Trail** | `scripts/ai_engine/context_trail.py` | Temporal briefing |
| **Large File Reader** | `scripts/ai_engine/large_file_reader.py` | Chunking, MapReduce |
| **Context Bootloader** | `packages/context_bootloader/` | Intelligent context loading, MCP integration |

---

### 4. Agent System (8 systems)

| System | Path | Purpose |
|--------|------|---------|
| **Genomes** | `.agent/genomes/` | 21 genome files — identity, role, overlays |
| **Agent** | `packages/agent/` | Aether agent, consciousness wrapper |
| **Specialist System** | `packages/specialist_system/` | Domain expert agents, auto-activation |
| **Capability Awareness** | `packages/capability_awareness/` | Domain expert framework |
| **Agent Spawner** | `scripts/ai_engine/agent_spawner.py` | Specialist deployment |
| **Agent Runtime** | `scripts/ai_engine/agent_runtime.py` | Plan execution |
| **Agent Mesh** | `scripts/ai_engine/agent_mesh.py` | Affinity, rank |
| **Roundtable** | `scripts/ai_engine/roundtable.py` | Multi-agent deliberation |

---

### 5. MCP & Transport (6 systems)

| System | Path | Purpose |
|--------|------|---------|
| **Lucid MCP Server** | `lucid_mcp_server.py` (root) | Main monolith — 84+ tools, JSON-RPC stdio |
| **MCP HTTP Fallback** | `scripts/mcp_http_fallback_server.py` | HTTP bridge :5001, /mcp/execute |
| **MCP RAG Proxy** | `packages/mcp_rag_proxy/` | Context-aware tool selection, RAG |
| **MCP Server** (legacy) | `packages/mcp_server/` | FastAPI MCP on :8000 |
| **MCP Data Integration** | `packages/mcp_data_integration/` | MCP + AETHER_MEMORY integration |
| **MCP Debugging** | `packages/mcp_debugging_system/` | MCP config/connectivity debugging |
| **Daemon RAG System** | `daemon_rag_system/` (root) | Task classification, intent inference |

---

### 6. UI & Cockpit (6 systems)

| System | Path | Purpose |
|--------|------|---------|
| **JOC** (Joint Operations Center) | `packages/joc/` | React/Vite command surface, dispatch, session |
| **IDE Chat App** | `packages/ide_chat_app/` | Electron app, AI chat panel |
| **AIMOS Mobile App** | `packages/aimos_mobile_app/` | Mobile AIM-OS interface |
| **JOC Tournament** | `packages/joc-tournament/` | Multi-agent UI competition |
| **Browser Automation Service** | `packages/browser-automation-service/` | Browser lifecycle, automation APIs :5002 |
| **Lucid Core Console** | `packages/lucid_core_console/` | Console UI |

---

### 7. Consciousness & Safety (12 systems)

| System | Path | Purpose |
|--------|------|---------|
| **SCOR** (Sanity Core) | `packages/scor/` | Invariant checks, baseline probes, manipulation detection |
| **Consciousness Analyzer** | `packages/consciousness_analyzer/` | Consciousness systems analysis |
| **Consciousness Creativity** | `packages/consciousness_creativity_engine/` | Novel ideas, creative expression |
| **Consciousness Error Learning** | `packages/consciousness_error_learning/` | Error capture, analysis, learning |
| **Consciousness Learning** | `packages/consciousness_learning_engine/` | Self-directed learning |
| **Consciousness Optimization** | `packages/consciousness_optimization_detector/` | Performance monitoring |
| **Safety Systems** | `packages/safety_systems/` | Manager AI, line removal, protocol |
| **Temporal Consciousness** | `packages/temporal_consciousness/` | Timeline, goals, chains provenance |
| **Holographic Memory** | `packages/holographic_memory/` | Distributed associative memory |
| **SIS** (Self-Improvement) | `packages/sis/` | Meta-cognitive analysis, auditing, learning |

---

### 8. Supporting Packages (25+ systems)

| System | Path | Purpose |
|--------|------|---------|
| **Router** | `packages/router/` | Intelligent tool selection, Scout LLM, Bandit |
| **Router API Server** | `packages/router_api_server/` | FastAPI Router + Log-Sentinels backend |
| **Unified** | `packages/unified/` | Unified Router + Log-Sentinels, closed-loop |
| **Prompt Chains** | `packages/prompt_chains/` | Workflow graph data models |
| **Prompt Chain Executor** | `packages/prompt_chain_executor/` | Chain execution, graph traversal |
| **LLM Client** | `packages/llm_client/` | Multi-provider LLM interface |
| **API Service Registry** | `packages/api_service_registry/` | External APIs (Meshy, ElevenLabs) |
| **Intent Classification** | `packages/intent_classification/` | User input → mission profiles |
| **Orchestration Builder** | `packages/orchestration_builder/` | LLM orchestration build/execute |
| **Autonomous Protocol** | `packages/autonomous_protocol/` | Start/stop/pause, checklist |
| **Autonomous Research Dream** | `packages/autonomous_research_dream/` | Recursive analysis, research |
| **APOE Runner** | `packages/apoe_runner/` | ACL plan execution |
| **NL Tags** | `packages/nl_tags/` | Natural language code tagging |
| **ICIP Search** | `packages/icip_search/` | Semantic code search, FAISS |
| **DeepSearch** | `packages/deepsearch/` | Sovereign local intelligence, trust scoring |
| **Doc Builder** | `packages/doc_builder/` | Markdown from structured seeds |
| **Log Sentinels** | `packages/log_sentinels/` | Log analysis, hybrid cloud/local |
| **Meta Optimizer** | `packages/meta_optimizer/` | Vision tensors, gating |
| **Meta Reasoning** | `packages/meta_reasoning/` | Explicit LLM reasoning |
| **Quaternion Kernel** | `packages/quaternion_kernel/` | 4D quaternion scene kernel |
| **Quaternion Math** | `packages/quaternion_math/` | Quaternion math library |
| **Schemas** | `packages/schemas/` | MPD, BitemporalEdge, consolidated models |
| **AI Collaboration** | `packages/ai_collaboration/` | AI-to-AI messaging |
| **Shared** | `packages/shared/` | Shared utilities |
| **Integration Tests** | `packages/integration_tests/` | Test suite |

---

### 9. UI Packages (Additional)

| System | Path | Purpose |
|--------|------|---------|
| **Lucid Document Editor** | `packages/lucid_document_editor/` | Document editing |
| **Advanced Monaco Editor** | `packages/advanced_monaco_editor/` | Code editor with NL details |
| **Lumin Snap System** | `packages/lumin_snap_system/` | Snapshot system |
| **Lucid Orchestrator** | `packages/lucid_orchestrator/` | Orchestration UI |
| **Plix** | `packages/plix/` | PLIx language, compiler |
| **IGODN** | `packages/igodn/` | Graph visualization |
| **AIMOS SDK** | `packages/aimos-sdk/` | SDK for AIM-OS apps |

---

### 10. Apps (15+)

| App | Path | Purpose |
|-----|------|---------|
| **Echo Forge Loop** | `apps/echo-forge-loop/` | AIM-OS orchestration app — chat + dashboard, Supabase |
| **System Atlas** | `apps/system-atlas/` | System map visualization |
| **ProEarth** | `apps/ProEarth/` | World editor |
| **Planet Engine** | `apps/planet-engine/` | Planet/terrain |
| **Globe** | `apps/Globe/` | Globe visualization |
| **OPUS** | `apps/OPUStree/`, `OPUS_ONBOARDING_PACK/` | OPUS onboarding |
| **MASTER_ORCHESTRATION** | `apps/MASTER_ORCHESTRATION/` | Orchestration |
| **HyperRealH20Monolith** | `apps/HyperRealH20Monolith/` | Water rendering |
| **OpusMagnusWater** | `apps/OpusMagnusWater/` | Water rendering |
| **lucidimage** | `apps/lucidimage/` | Image processing |
| **OPUS** variants | `OPUStree`, `OPUS_ONBOARDING_PACK` | Onboarding variants |

---

### 11. Scripts & Utilities (50+)

| Category | Path | Key Scripts |
|----------|------|-------------|
| **MCP Control** | `scripts/` | mcp_http_fallback_server.py, mcp_sse_server.py, mcp_bridge.py, mcp_transport_smoke.py |
| **Launchers** | `scripts/launchers/` | START_BAS_DETERMINISTIC.ps1, start_codex_agent.ps1 |
| **MCP Control** | `scripts/` | mcp_control.ps1, run_mcp_http_fallback.ps1 |
| **Sentinel** | `scripts/` | sentinel.py, sentinel_telemetry.py, sentinel_nexus.py, sentinel_chronicle.py, sentinel_phantom.py, sentinel_mcp_governance.py, sentinel_host_baselines.py |
| **Agent Comms** | `scripts/agent_comms/` | render_codex_activation.py, identity_registry.py |
| **AIMOS Relay** | `scripts/aimos_relay/` | relay_bridge.py |
| **Seer** | `scripts/seer/` | discovery, capture, gemini_integration, automation |
| **Documentation** | `scripts/` | generate_complete_visualization.py, generate_epic_atlas_mermaid.py, assemble_system_map.py |
| **Utilities** | `scripts/utilities/` | Various utilities |
| **HHNI** | `scripts/` | index_aimos_docs_for_hhni.py, hhni_schema_apply.py |
| **Verification** | `scripts/` | check_mcp_tool_parity.py, verify_mcp_tools.py |

---

### 12. Documentation & Knowledge (5 systems)

| System | Path | Purpose |
|--------|------|---------|
| **Knowledge Architecture** | `knowledge_architecture/` | Master concept map, SUPER_INDEX |
| **AETHER_MEMORY** | `knowledge_architecture/AETHER_MEMORY/` | AI consciousness memory |
| **SAM** (System Anatomy Mapping) | `knowledge_architecture/SAM/` | MASTER_* maps, sources |
| **Systems Docs** | `knowledge_architecture/systems/` | L0-L4 per system |
| **PROJECT_TRUTH** | `PROJECT_TRUTH/` | Canonical system index, evidence ledger |

---

### 13. Root-Level Systems (8)

| System | Path | Purpose |
|--------|------|---------|
| **Lucid MCP Server** | `lucid_mcp_server.py` | Main MCP monolith (root) |
| **Daemon RAG System** | `daemon_rag_system/` | RAG daemon, tool selection |
| **IDE Orchestration** | `ide_orchestration/` | DAC v2 prototype, IDE integration |
| **Cursor Addon** | `cursor-addon/` | Cursor IDE extension |
| **Context Capsule** | `context_capsule_wire_and_mapper_v1/` | Shadow sync, wire proof |
| **MCP Memory** | `mcp_memory/` | MCP memory persistence |
| **MCP Aether** | `mcp-aether/` | Aether MCP integration |
| **Goals** | `goals/` | GOAL_TREE.yaml, objectives |

---

## Summary Counts

| Domain | Systems | Packages | Scripts |
|--------|---------|----------|---------|
| Core Infrastructure | 9 | 9 | 0 |
| AI Engine | 28+ | 0 | 28+ |
| Context System | 6 | 1 | 5 |
| Agent System | 8 | 4 | 4 |
| MCP & Transport | 7 | 5 | 2 |
| UI & Cockpit | 6 | 6 | 0 |
| Consciousness & Safety | 10 | 10 | 0 |
| Supporting Packages | 25+ | 25+ | 0 |
| Apps | 15+ | 0 | 0 |
| Scripts & Utilities | 50+ | 0 | 50+ |
| Documentation | 5 | 0 | 0 |
| Root-Level | 8 | 0 | 0 |
| **Total** | **~170+** | **~60+** | **~90+** |

---

## Canonical References

- **AIMOS_MAJOR_SYSTEMS:** `docs/AIMOS_MAJOR_SYSTEMS.md`
- **00_MASTER_AIMOS_SYSTEM_MAP:** `knowledge_architecture/SAM/sources/00_MASTER_AIMOS_SYSTEM_MAP.md`
- **PROJECT_TRUTH:** `PROJECT_TRUTH/01_canonical_system_index.md`
- **SUPER_INDEX:** `knowledge_architecture/SUPER_INDEX.md`
- **Machine Registry:** `.agent/SYSTEM_REGISTRY.md` (Phase 26 crawl output)

---

*This index is the product of a full manual audit. It supersedes partial or stale indexes. Update when new systems are added.*
