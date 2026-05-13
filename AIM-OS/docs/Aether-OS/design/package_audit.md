# AIM-OS Package Audit — Complete Inventory

> Generated 2026-03-11 by Antigravity during Phase 1 audit.
> All findings verified from actual source code, not documentation.

## Summary

| Category | Count |
|----------|-------|
| **Python (proper init)** | ~33 |
| **Python (no init)** | 8 |
| **TypeScript/React** | 9 |
| **Rust** | 1 |
| **Total** | 68 + `__pycache__` |

---

## Core 7 (All Genuine — Deeply Interconnected)

| Package | Init | Exports | Lines | Status |
|---------|------|---------|-------|--------|
| `cmc_service` | ✅ (63L) | MemoryStore, BitemporalQueryEngine, AtomRepository, BatchProcessor, ConnectionPool, CacheManager | ~2K | **Active** — foundation for all MCP memory ops |
| `hhni` | ✅ (68L) | HierarchicalIndex, SemanticSearchEngine, DVNSPhysics, TwoStageRetriever, TokenBudgetManager, Compressor, ConflictResolver | ~2K | **Active** — powers MCP retrieve_memory |
| `vif` | ✅ (205L) | VIF, KappaGate, ECETracker, ReplayEngine, BandRouter + 7 integration modules (CMC, SEG, HHNI, SDFCVF, TCS, CAS, Audit) | ~3K | **Active** — powers MCP track_confidence |
| `apoe` | ✅ (143L) | ACLParser, PlanExecutor, RoleDispatcher, DEPPController, CompoundGate, ErrorRecovery, HITLManager, ParallelExecutor, StreamingExecutor | ~5K | **Active** — powers MCP create_plan |
| `cas` | ✅ (35L) | ActivationTracker, CategoryRecognizer, AttentionMonitor, FailureModeAnalyzer, IntrospectionProtocol | ~1K | **Active** — powers MCP run_cognitive_audit |
| `seg` | ✅ (155L) | SEGraph (NetworkX), Entity, Relation, Evidence, Contradiction + 6 optional integrations | ~2K | **Active** — powers MCP synthesize_knowledge |
| `sdfcvf` | ✅ (97L) | QuartetDetector, ParityCalculator, ParityGate, BlastRadiusResult, DORAMetrics + 8 system integrations | ~2K | **Active** — atomic evolution framework |

## Other Active Python Packages

| Package | Init | Files | Key Purpose |
|---------|------|-------|-------------|
| `agent` | ✅ | 6 | Agent framework |
| `ai_collaboration` | ✅ | 2 | AI-to-AI messaging |
| `api_service_registry` | ✅ | 1 | API registry |
| `apoe_runner` | ✅ | 5 | APOE launcher |
| `autonomous_research_dream` | ✅ | 7 | ARD system |
| `capability_awareness` | ✅ | 9 | Capability tracking |
| `deepsearch` | ✅ | 5 | Multi-layer search (⚠️ broken — not importable as MCP tool) |
| `doc_builder` | ✅ | 2 | Documentation builder |
| `holographic_memory` | ✅ | 6 | Holographic memory system |
| `icip_search` | ✅ | 5 | Semantic code search (⚠️ index not built) |
| `integration_tests` | ✅ | 12 | Cross-package tests |
| `intent_classification` | ✅ | 6 | Intent classification |
| `intuitive_intelligence_system` | ✅ | 11 | IIS — powers compute_intuition |
| `llm_client` | ✅ | 5 | LLM API client |
| `log_sentinels` | ✅ | 1 | Log monitoring |
| `meta_optimizer` | ✅ | 2 | Meta-optimization |
| `nl_tags` | ✅ | 12 | Natural language tagging |
| `orchestration_builder` | ✅ | 4 | Orchestration building |
| `prompt_chain_executor` | ✅ | 3 | Prompt chain execution |
| `quaternion_math` | ✅ | 1 (16K init) | Quaternion mathematics |
| `router` | ✅ | 1 | Request routing |
| `router_api_server` | ✅ | 3 | Router HTTP server |
| `schemas` | ✅ | 3 | Data schemas |
| `scor` | ✅ | 1 | Safety/invariant checking |
| `sis` | ✅ | 3 | System integration service |
| `specialist_system` | ✅ (43L) | SpecialistRegistry, RelevanceCalculator, ActivationSystem, WorkDetector, MathTools | Active — powers MCP specialist tools |
| `temporal_consciousness` | ✅ | 4 | Temporal awareness |
| `unified` | ✅ | 2 | Unified interface |

## Packages Missing `__init__.py` ⚠️

| Package | Files | Notes |
|---------|-------|-------|
| `autonomous_protocol` | 3 py | Should have init |
| `context_bootloader` | 2 py | Should have init |
| `jarvis_injector` | 0 py | Possibly abandoned |
| `meta_reasoning` | 1 py | Needs init |
| `prompt_chains` | 0 py | May be TS or empty |
| `safety_systems` | 6 py | Should have init |
| `shared` | 0 py | May be TS or empty |
| `timeline_context_system` | **61 py (43,846 lines!)** | **Biggest package** — needs init urgently |

## TypeScript/React Packages

| Package | Framework | Notes |
|---------|-----------|-------|
| `advanced_monaco_editor` | TS | Monaco editor customization |
| `aimos_mobile_app` | TS | Mobile app |
| `aimos-sdk` | TS | AIM-OS SDK |
| `browser-automation-service` | TS | Browser automation |
| `ide_chat_app` | TS | IDE chat interface |
| `igodn` | TS | Unknown purpose |
| `joc` | TS | JOC system |
| `lumin_snap_system` | TS | UI snapshot system |
| `plix` | TS | Unknown purpose |

## Rust Package

| Package | Notes |
|---------|-------|
| `quaternion_kernel` | Rust (Cargo.toml). **27 markdown status docs** — worst doc drift in repo |

## Overlap Groups — Consolidation Needed

### consciousness_* (5 packages) → MERGE

| Package | Main Files | Purpose | Action |
|---------|-----------|---------|--------|
| `consciousness_analyzer` | performance_analyzer (23K), optimization_advisor (16K), metrics_collector (15K), health_monitor (12K), dashboard (10K) | Analyze + optimize consciousness | **MERGE INTO ONE** |
| `consciousness_optimization_detector` | system_auditor (28K) | Detect optimization opportunities | ↑ merge target |
| `consciousness_creativity_engine` | idea_generator (25K), creative_expression (22K) | Creative expression | Keep separate |
| `consciousness_error_learning` | error_capturer (12K) | Learn from errors | Consider merge ↓ |
| `consciousness_learning_engine` | self_directed_learner (27K) | Self-directed learning | Consider merge ↑ |

### MCP Server Copies → DELETE EXTRAS

| File | Lines | Action |
|------|-------|--------|
| `lucid_mcp_server.py` (root) | 11,138 | **KEEP — active server** |
| `context_capsule_.../lucid_mcp_server.py` | 10,702 | **DELETE — dangerous near-duplicate** |
| `archive/minimal_mcp_server.py` | 146 | Already in archive — leave |
| `archive/run_mcp_server.py` | 28 | Already in archive — leave |
| `archive/test_advanced_mcp_server.py` | 139 | Already in archive — leave |
| `archive/test_mcp_server_local.py` | 192 | Already in archive — leave |
| `daemon_rag_system/daemon_rag_mcp_server.py` | 400 | **ARCHIVE** |
