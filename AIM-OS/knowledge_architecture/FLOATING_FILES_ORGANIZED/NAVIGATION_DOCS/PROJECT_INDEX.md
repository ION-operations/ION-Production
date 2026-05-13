## AIM-OS Project Index (Docs, Code, Hierarchy)

Purpose: A concise, dependency-free map of the project with a clear hierarchy and summaries of the main docs and code we own. Excludes node_modules and third-party vendored assets.

Last updated: 2025-10-30

---

### Top-level structure

- knowledge_architecture: Documentation standards, system L0–L4 docs, navigation, workflow orchestration, timelines, and rules.
- packages: First-party code packages (Python, TypeScript, React) for core systems and apps.
- daemon_rag_system: Python Daemon/RAG integration system orchestrating tool selection and servers.
- goals: Authoritative goal tree and status files.
- audits, archive, plans, projects, analysis: Process artifacts, historical logs, audits, plans, and analyses.
- deployment, deploy, bootloaders: Deployment configs and bootstrap YAMLs.
- Testing, scripts, snapshots, test_mcp_configs: Test artifacts, utilities, and snapshots.

---

### knowledge_architecture (key files and directories)

- HIERARCHICAL_NAVIGATION_INDEX.md: Master navigation index routing readers by confidence to L0–L4 for 11+ systems and 32 standards, with status and integration map.
- SYSTEM_HIERARCHY.md: High-level system hierarchy spec (see also Perfect System Hierarchy standard below).
- PERFECT_*.md family: Complete documentation standards (L0–L6, System Map/Index, Metadata, Validation, Timeline, KPI, Project Plan, etc.).
- WORKFLOW_ORCHESTRATION/
  - task_dependency_map.yaml: YAML DAG connecting goals→systems→tasks with confidence/priority routing for autonomous work.
- NAVIGATION/
  - cross_system_connections.yaml: Cross-system dependency map for navigation.
- systems/
  - global_user_rules/: L0–L4 for Global User Rules.
  - branch_reasoning_system/: L0–L4 branch reasoning docs.
  - consciousness_enhancement/: L0–L4 docs.
  - ai_collaboration_system/: L0–L4 docs.
  - dynamic_cursor_rules_system/: scripts and loader for dynamic rules.
  - (See HIERARCHICAL_NAVIGATION_INDEX.md for the full systems list and links.)
 
Summarized highlights (new):

- HIERARCHICAL_NAVIGATION_INDEX.md: Complete, authoritative routing and status for all systems, confidence-based navigation, and integration map.
- WORKFLOW_ORCHESTRATION/task_dependency_map.yaml: Living DAG used for autonomous routing; encodes objectives, systems, tasks, KRs, routing rules, and dependencies.

---

### daemon_rag_system (Python)

- daemon_rag_system.py: Main daemon integrating context analysis, tool selection, RAG, server management, performance monitoring, learning, and resource management. Defines config/metrics, request processing pipeline, server orchestration by selected tools, and status/metrics export.
- ah_protocol/, rag_system/, tool_selection_engine/, tool_registry/, server_manager/, performance_monitor/, learning_system/, resource_manager/: Component subsystems used by the daemon.

Summarized highlights (new):

- daemon_rag_system.py: Orchestrates MCP tool selection under a 40-tool limit with timing budgets; manages servers required by selected tools; tracks metrics; supports background processing via thread loop.

---

### goals

- GOAL_TREE.yaml: Authoritative goal hierarchy for AIM-OS v0.3; objectives for CMC reliability, HHNI indexing, validation framework, infra reliability, and MCP data integration with measurable KRs and artifacts.
- GOAL_TREE_UPDATED.yaml: Updated variant if present.

Summarized highlights (new):

- GOAL_TREE.yaml: Defines objectives/KRs, owners, target dates, invariants, acceptance artifacts, and code links (e.g., CMC service files, HHNI schemas).

---

### packages (first-party code)

- cas/ (Python)
  - __init__.py: CAS package exports trackers and analyzers for activation, category, attention, failure modes, and introspection.
  - activation.py: Computes "hot vs cold" activation across principles/docs using recency, frequency, salience, and load; captures snapshots and warnings.
  - tests/: Unit tests for CAS.

- mcp_data_integration/ (Python): Bridges MCP tools to data, indexing, visualization, search, and integrations (confidence, timeline, goals).

- lucid_orchestrator/ (TypeScript): Orchestration engines, VS Code extension, and daemon clients for Lucid workflows.

- ide_chat_app/ (React/TS): IDE UI with Monaco, Lucid Orchestrator views, collaboration, timelines, code/docs viewers, and dashboards.
  - src/components/Advanced IDE modules (see advanced_monaco_editor and Lucid components).
  - src/components/IDELayout.tsx: Main IDE layout, panel orchestration, and docked tools.

- advanced_monaco_editor/ (React/TS)
  - src/components/AdvancedMonacoEditor.tsx: Advanced Monaco Editor integrating symbol detection, code analysis, AIM-OS integration, themes, security, validation, and rich UI (dropdowns, tooltips, context menu).
  - src/services/*: SymbolDetectionService, CodeAnalysisService, AIMOSIntegrationService, Theme/Performance/Security/Validation services.
  - tests/: Comprehensive unit and integration tests.

Other notable packages: intent_classification (Python), timeline_context_system (Python), mcp_rag_proxy (Python), lucid_core_console (TS), scor (Python), etc.

Summarized highlights (new):

- cas/__init__.py: Declares package API and metadata for CAS.
- cas/activation.py: Activation tracking formulas, state capture, and warnings.
- advanced_monaco_editor/src/components/AdvancedMonacoEditor.tsx: Central editor component wiring all services and UI behaviors; supports AIM-OS endpoints and analysis flows.
- ide_chat_app/src/components/IDELayout.tsx: Full IDE shell with left/right panels, center editors, bottom drawers, and Lucid orchestration views.

- mcp_data_integration/data_indexer.py: SQLite-backed indexer for `AETHER_MEMORY` markdown; extracts metadata/tags/categories, builds a term index with context windows, exposes search and stats, and handles resilient decoding + size limits.

- mcp_rag_proxy/rag_proxy.py: TF‑IDF + cosine similarity RAG proxy over MCP tool metadata; ranks tools by query relevance and a consciousness-weighted factor; returns recommendations, quality analysis, and system stats.

- timeline_context_system/prompt_context_tracker.py: Captures per-prompt context snapshots, computes evolution, builds timeline entries with confidence metrics, and persists via CMC or file fallback; supports summaries and range queries.

- lucid_orchestrator/extension/src/extension.ts: VS Code extension activation; connects to daemon, registers fold providers (spec/blueprint/timeline) and change proposals, and updates gutter decorations via a provider.

---

### deployment, deploy, bootloaders

- deployment/docker-compose.yml and deploy/docker-compose.yml: Container orchestration configs.
- bootloaders/*.yaml: Boot sequences for VIF and safety systems.

---

### audits, archive, plans, projects, analysis

- audits/2025-10-29/COMPREHENSIVE_DOCUMENTATION_SYSTEMS_AUDIT.md: Documentation audit of systems and standards.
- plans/*: Execution plans for standards rollout, MCP timeline/goals, organization moves, etc.
- archive/*: Historical achievements, progress summaries, design docs.
- projects/mcp_data_integration/*: Epic summary and artifacts for the MCP data integration effort.
- analysis/data_index.md: Indexes and analyses.

---

### Testing, scripts, snapshots

- Testing/: Scenario flows and orchestration samples in YAML; UI/testing artifacts.
- scripts/: Utility scripts (e.g., verify_mcp_tools.py).
- snapshots/: Script snapshots and backups.
- test_mcp_configs/: MCP configuration JSONs for testing.

---

### Newly created summaries (grounded by source reads)

- knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md
  - Complete L0–L4 routing for 11 systems and 32 standards; confidence-guided reading paths; integration and status maps for core systems (CMC, HHNI, VIF, APOE, SEG, SDF-CVF, CAS) and enhanced systems (Timeline, Cross-Model, Dual-Prompt, MCP). Quick references and completion statuses included.

- knowledge_architecture/WORKFLOW_ORCHESTRATION/task_dependency_map.yaml
  - YAML DAG connecting north_star→objectives→systems→tasks→key_results with confidence/priority/dependency routing. Used for autonomous task selection and progress tracking.

- daemon_rag_system/daemon_rag_system.py
  - Defines DaemonRAGSystem with config/metrics. Pipeline: context analysis → tool selection → server management → optional learning, under 40-tool limit and latency budgets. Exports status, metrics, RAG statistics, and config.

- goals/GOAL_TREE.yaml
  - Authoritative goals/KRs and artifacts for v0.3 (CMC reliability; HHNI indexing; validation framework; infra reliability; MCP data integration). Includes owners, target dates, invariants, acceptance references, and code artifacts.

- packages/cas/__init__.py
  - CAS package API exporting activation, category, attention, failure mode, and introspection components; versioned metadata.

- packages/cas/activation.py
  - Activation tracking with recency/frequency/salience/load; snapshot capture; cold-principle detection; simple embedding and cosine similarity helpers for salience.

- packages/advanced_monaco_editor/src/components/AdvancedMonacoEditor.tsx
  - Advanced Monaco wrapper integrating services for symbol detection, analysis, AIM-OS integration, themes, performance, security, and validation; rich UI for dropdowns, context menus, tooltips; real-time/background analysis hooks.

- packages/ide_chat_app/src/components/IDELayout.tsx
  - Main IDE shell managing panels, drawers, chats, orchestration and code/docs viewers; integrates Lucid editor and orchestrator components with flexible layout and controls.

---

### Notes

- This index intentionally excludes node_modules and third-party vendored files.
- For the complete standards list and cross-links, see `knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md`.
- Next step: expand per-directory coverage with brief summaries for remaining first-party files (Python/TS/MD) and link them here.


