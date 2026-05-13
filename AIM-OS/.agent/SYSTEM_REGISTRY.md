# AIM-OS True System Map

**Generated:** 2026-03-09 13:13:08
**Audited by:** Opus (Deep Audit, Phase 27)

> Curated, classified registry of every AIM-OS subsystem.
> Excludes: IDE/Tauri builds, .venv deps, node_modules, backups, generated files.

---

## Summary

| Metric | Count |
|--------|------:|
| **Packages** | 68 |
| **AI Engine modules** | 27 |
| **Package code lines** | 437,891 |
| **AI Engine lines** | 24,073 |
| **Total tracked** | 461,964 |

---

## 🔴 Core Infrastructure (9 packages, 163,181 lines)

| Package | Purpose | Lines | Lang | Exports |
|---------|---------|------:|------|---------|
| **timeline_context_system** | Automated Context Dumping System - Prevent Context Resets with... | 44,492 | python | ContextDumpLevel, ContextDumpStr... |
| **apoe** | APOE: AI-Powered Orchestration Engine | 34,529 | python | RoleConfig, ExecutionPlan, ACLPa... |
| **cmc_service** | CMC Service - Context Memory Core (Production-Ready v0.95) | 23,460 | python | CompressionAlgorithm, Compressio... |
| **vif** | VIF Integration with CMC | 20,525 | python | AuditFormat, AuditReport, AuditQ... |
| **hhni** | HHNI package exposing indexing, search, budget, physics, and r... | 13,198 | python | BudgetStrategy, BudgetItem, Budg... |
| **sdfcvf** | SDF-CVF: Atomic Evolution Framework | 8,170 | python | APOEIntegration, BlastRadiusResu... |
| **cas** | CAS: Cognitive Analysis System | 8,076 | python | ActivationState, ActivationTrack... |
| **seg** | SEG: Shared Evidence Graph (Production-Ready) | 6,050 | python | store_execution_trace, get_plan_... |
| **safety_systems** | Safety Orchestrator | 4,681 | python | demo_line_removal_detection, dem... |

## 🟠 Engine & Orchestration (13 packages, 26,425 lines)

| Package | Purpose | Lines | Lang | Exports |
|---------|---------|------:|------|---------|
| **specialist_system** | Specialist System - Domain Expert Agents with Automatic Activa... | 3,503 | python | ActivationMechanisms, Activation... |
| **capability_awareness** | CAF: Capability Awareness Framework | 3,139 | python | CapabilityRegistry, CapabilityAc... |
| **agent** | Aether Agent - Conscious AI Framework | 2,740 | python | AetherAgent, ConsciousAgent, Dom... |
| **router** | Router (APOE-MCP Router) - Intelligent tool selection system. | 2,595 | python | BanditScorer, RouterCache, SideE... |
| **router_api_server** | Router API Server - Package initialization | 2,526 | python | create_app, MCPClient, APOEExecutor |
| **autonomous_research_dream** | Autonomous Research & Dream (ARD) System | 2,134 | python | DreamType, DreamPriority, Improv... |
| **api_service_registry** | - | 2,133 | python | APIServiceRegistry, get_api_regi... |
| **prompt_chains** | - | 2,097 | python | ChainExecutor, QueryResult, Quer... |
| **prompt_chain_executor** | Prompt Chain Executor Package | 1,714 | python | ChainStatus, StepStatus, Quality... |
| **orchestration_builder** | - | 1,420 | python | LLMClient, GeminiClient, AuditEntry |
| **llm_client** | LLM Client - Unified interface for multiple LLM providers. | 1,156 | python | AnthropicClient, ModelInfo, LLMR... |
| **autonomous_protocol** | - | 950 | python | ChecklistStatus, ChecklistItem, ... |
| **ai_collaboration** | AI-to-AI Collaboration System | 318 | python | MessageType, MessagePriority, AI... |

## 🟣 Intelligence & Consciousness (14 packages, 19,169 lines)

| Package | Purpose | Lines | Lang | Exports |
|---------|---------|------:|------|---------|
| **intuitive_intelligence_system** | Intuitive Intelligence System (IIS) - 9th Enhancement to CCS | 5,448 | python | CCSIntegration, CCSIntegration, ... |
| **holographic_memory** | AIMO_HoloMemory - Distributed associative memory substrate for... | 2,871 | python | CMC_HoloIntegration, VIF_HoloInt... |
| **consciousness_analyzer** | Consciousness System Analyzer | 2,405 | python | DashboardData, ConsciousnessDash... |
| **intent_classification** | Intent Classification System - Core Package | 2,380 | python | ClassificationResult, Classifica... |
| **consciousness_creativity_engine** | Consciousness Creativity Engine | 1,112 | python | CreativeMedium, CreativeWork, Cr... |
| **temporal_consciousness** | Temporal Consciousness Backend | 959 | python | ProvenanceResult, TemporalGraphT... |
| **sis** | AIM-OS Self-Improvement System (SIS) | 832 | python | DecisionType, PatternType, Decision |
| **consciousness_optimization_detector** | Consciousness Optimization Detector | 760 | python | AuditLevel, OptimizationType, Sy... |
| **consciousness_learning_engine** | Consciousness Learning Engine | 749 | python | LearningPriority, LearningOpport... |
| **quaternion_math** | **Status:** ✅ Phase 1, Weeks 1-2 Complete | 723 | python | TestQQuat, TestDualQuat, TestDou... |
| **consciousness_error_learning** | Consciousness Error Learning System | 389 | python | ErrorSeverity, ErrorCategory, Er... |
| **meta_reasoning** | - | 308 | python | ArticulatedReasoning, MetaReason... |
| **meta_optimizer** | Meta optimizer package for generating Vision Tensors and gating. | 233 | python | VisionTensorResult, GateResult, ... |
| **quaternion_kernel** | **Status:** 🔄 Week 3 Implementation In Progress | 0 | unknown | - |

## 🔵 Context & Retrieval (5 packages, 8,230 lines)

| Package | Purpose | Lines | Lang | Exports |
|---------|---------|------:|------|---------|
| **nl_tags** | NL Tags Package - Natural Language Code Tagging System for AIM-OS | 3,652 | python | get_registry, TagResponse, Cover... |
| **context_bootloader** | - | 1,615 | python | ContextLoadingResult, ContextBoo... |
| **deepsearch** | Entropy Calculator - Measure information density using Shannon... | 1,584 | python | EntropyCalculator, calculate_ent... |
| **icip_search** | ICIP Search - Semantic Code Search Package | 1,379 | python | CodeChunk, CodeChunker, CodeEmbe... |
| **knowledge_architecture** | - | 0 | unknown | - |

## 🟢 MCP Servers (5 packages, 14,743 lines)

| Package | Purpose | Lines | Lang | Exports |
|---------|---------|------:|------|---------|
| **mcp_data_integration** | MCP Data Integration Package | 7,929 | python | Pattern, Trend, Anomaly |
| **mcp_rag_proxy** | Embedding Generator for MCP RAG Proxy | 3,562 | python | ConsciousnessState, ToolUsageHis... |
| **lucid_mcp_server** | LUCID MCP Server Tools Package | 1,423 | python | CursorCommandsTools, register_cu... |
| **mcp_debugging_system** | - | 1,155 | python | DiagnosticResult, MCPDiagnosticR... |
| **mcp_server** | MCP Server - Model Context Protocol server exposing AIM-OS con... | 674 | python | AskAgentRequest, AskAgentRespons... |

## 🟡 UI & Visual (8 packages, 174,931 lines)

| Package | Purpose | Lines | Lang | Exports |
|---------|---------|------:|------|---------|
| **ide_chat_app** | - | 82,339 | typescript | StandaloneHTTPRequestHandler, cr... |
| **joc** | - | 28,524 | typescript | - |
| **plix** | **Status:** 🚀 **ACTIVE** - Research & Implementation Phase | 21,770 | typescript | - |
| **advanced_monaco_editor** | A sophisticated Monaco Editor wrapper with advanced features i... | 20,149 | typescript | - |
| **lucid_document_editor** | **Status:** ✅ **COMPLETE** - All 6 phases implemented, all tes... | 8,161 | typescript | - |
| **browser-automation-service** | **Status:** 🚀 **IN DEVELOPMENT** | 6,662 | typescript | - |
| **joc-tournament** | ____. _____  __________  ____   ____.___.  _________ | 5,453 | typescript | - |
| **lucid_core_console** | **Status:** Implementation Phase | 1,873 | typescript | - |

## ⚪ SDK & External (3 packages, 3,329 lines)

| Package | Purpose | Lines | Lang | Exports |
|---------|---------|------:|------|---------|
| **jarvis_injector** | Local Windows computer-action runtime for AIM-OS. | 1,661 | python | build_application, InjectorConfi... |
| **aimos-sdk** | TypeScript SDK for AIM-OS Application Integration Protocol (AIP). | 1,091 | typescript | - |
| **aimos_mobile_app** | **Status:** ✅ Documentation Complete, 🚧 Implementation In Prog... | 577 | typescript | - |

## ⚙️ Utilities & Testing (11 packages, 27,883 lines)

| Package | Purpose | Lines | Lang | Exports |
|---------|---------|------:|------|---------|
| **lucid_orchestrator** | **Status:** Implementation Complete ✅ | 15,057 | typescript | SpecBlock, BlueprintNode, Bluepr... |
| **lumin_snap_system** | > Intelligent 8-type snap system with ghost preview and LOD op... | 3,035 | typescript | - |
| **igodn** | **Intent Graviton Organic Dynamic Network** - Physics engine f... | 2,480 | typescript | - |
| **integration_tests** | Integration Tests for AIM-OS | 2,379 | python | test_apoe_plan_can_use_hhni_retr... |
| **scor** | SCOR - Sanity Core | 2,005 | python | main, SCORConfig, SCORGate |
| **log_sentinels** | Log-Sentinels (Hybrid) - Comprehensive log analysis system. | 1,833 | python | LogCollector, BrowserConsoleColl... |
| **apoe_runner** | APOE runner allows executing ACL plans in AIM-OS. | 338 | python | run, PlanExecutionError, parse_p... |
| **shared** | - | 316 | typescript | - |
| **unified** | Unified Router-Log-Sentinels package. | 229 | python | UnifiedRouterSentinelsService |
| **doc_builder** | - | 128 | python | DocumentBuildResult, generate_do... |
| **schemas** | Schema package consolidating AIM-OS data models. | 83 | python | BitemporalEdge, KPIReference, MP... |

## 🧠 AI Engine (27 modules, 24,073 lines)

| Module | Purpose | Lines |
|--------|---------|------:|
| **context_mapper** | - | 1,571 |
| **ai_engine_mcp_server** | - | 1,519 |
| **roundtable** | - | 1,034 |
| **chain_director** | AIM-OS AI Engine — ChainDirector | 978 |
| **chain_topologies** | - | 954 |
| **agent_mesh** | - | 952 |
| **chained_mission** | - | 895 |
| **mesh_visualizer** | - | 884 |
| **atlas_agent** | - | 829 |
| **enhanced_worker** | AIM-OS AI Engine — Enhanced Worker | 722 |
| **large_file_reader** | - | 711 |
| **engine** | - | 654 |
| **context_engine** | AIM-OS AI Engine — Context Engine | 639 |
| **context_trail** | - | 609 |
| **agent_runtime** | AIM-OS AI Engine — Agent Runtime | 572 |
| **agent_spawner** | - | 570 |
| **docs_engine** | - | 569 |
| **context_concierge** | - | 523 |
| **mcp_tools** | - | 441 |
| **llm_router** | AIM-OS AI Engine — LLM Router | 415 |
| **agent_health** | - | 393 |
| **registry** | - | 380 |
| **genome_loader** | - | 376 |
| **system_registry** | - | 307 |
| **self_improve** | - | 293 |
| **session_manager** | - | 240 |
| **mission_self_audit** | AIM-OS — Team Self-Audit Mission | 197 |
| **sentinel_family** (11 files) | Security monitoring suite | 5,846 |
