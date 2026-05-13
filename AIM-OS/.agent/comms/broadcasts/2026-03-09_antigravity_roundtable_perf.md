# Roundtable Minutes

**Topic:** Perf
**Question:** CMC memory
**Agents:** 9/12 contributed
**Collective Context:** ~230,437 tokens
**Duration:** 26ms

## AGENT-CMC (relevance: 0.90)
**AGENT-CMC** — CMC (Context Memory Core)
Domain: 17,277 tokens of context loaded
Relevance: 0.90

Relevant knowledge (138 lines):
title: "CMC Executive Summary"
description: "100-word executive summary of Context Memory Core"
audience: "executives, quick reference"
confidence_threshold: 0.80
status: "complete"
tags: ["cmc", "core", "memory", "bitemporal", "t0-t6", "transitional"]
dependencies: []
related_docs: ["cmc_T1_overview", "system.map.lucid.json5"]

# CMC (Context Memory Core) – T0 Executive Summary (≈100 words)
CMC provides structured, bitemporal memory for AI consciousness. It stores information with both transaction time and valid time, enabling time‑travel queries and perfect provenance. CMC integrates with HHNI for retrieval, VIF for verification/witnesses, and SEG for knowledge synthesis, underpinning APOE orchestration and SDF‑CVF quality. This T‑level doc reflects the newest standards (templates, metadata, gates) without modifying legacy L‑level docs. After review, this will become the canonical executive summary. See system maps and indices for relationships and navigation; use the validation gate to confirm completeness before cutover.
### `memory_store.py` (810 lines)
- **MemoryStore** — Deterministic memory store with optional SQLite backend.
- **_NoOpDGraphClient** — No-op DGraph client when server unavailable. Allows HHNI indexing to complete (Qdrant vectors only).
- `_utc_now_iso()`
- `_datetime_to_iso()`
- `_ensure_hhni_collections()` — Create HHNI collections if missing (required for in-memory Qdrant).
### `memory_store_TAGGED.py` (679 lines)
- `_log_extra()`
- `tmp_store()` — Create a temporary MemoryStore for testing.
- `mock_hhni_clients()` — Mock DGraph and Qdrant clients for HHNI testing.
- `test_e2e_atom_creation_and_retrieval()` — Test: Create atom → List atoms → Verify content
### `test_memory_and_governance.py` (123 lines)
- `repository()`
- `test_memory_persistence_across_sessions()`
- `test_dependency_degree_limits()`
### `test_me

## AGENT-SEG (relevance: 0.40)
**AGENT-SEG** — SEG (Shared Evidence Graph)
Domain: 16,504 tokens of context loaded
Relevance: 0.40

Relevant knowledge (24 lines):
      direction: "bidirectional",
      connectsToSystem: "cmc.contextMemoryCore",
      protocol: "internal_api",
      whatIsExchanged: [
      fromPort: "cmcIntegration",
      toSystem: "cmc.contextMemoryCore",
      type: "provides_provenance_data",
      data_flow: "atoms \u2192 graph_nodes",
      relationship: "SEG stores graph nodes and provenance edges in CMC",
      whenToUse: "When implementing graph storage or understanding memory persistence",
      docs: [
        "systems/cmc/T2_architecture.md#seg-integration",
      "direction": "bidirectional",
      "connectsToSystemId": "cmc.contextMemoryCore",
      "protocol": "internal_api",
      "data": ["provenance_edges", "graph_nodes", "evidence_links"],
- ✅ Contradiction detection (find conflicting claims)
- ✅ NetworkX backend (fast, in-memory)
- ✅ **7 Integration Modules:** CMC, VIF, HHNI, APOE, SDF-CVF, CAS, TCS

from seg import Evidence, SEGraph
from cmc_service import MemoryStore
cmc_store = MemoryStore("./data")
graph = SEGraph()

## AGENT-HHNI (relevance: 0.40)
**AGENT-HHNI** — HHNI (Hierarchical Hypergraph Neural Index)
Domain: 17,736 tokens of context loaded
Relevance: 0.40

Relevant knowledge (20 lines):
- **TagPriorityVector** (0 methods)
- **HHNINode** — In-memory representation of a HHNI node prior to persistence.
- `utc_now()`
- `sha256_hex()`

### `test_memory_store_integration.py` (79 lines)
- `tmp_store()`
HHNI is the Hierarchical Hypergraph Neural Index that retrieves and organizes context using physics‑guided optimization. It builds a fractal hierarchy and uses DVNS forces to compress and de‑duplicate context under token budgets. HHNI integrates with CMC for bitemporal memory, VIF for verification, SEG for synthesis, and APOE for orchestration. This T‑level executive reflects the new documentation standards without changing legacy L‑level content. After review, it will replace the existing executive. See system maps and indices for relationships; run the validation gate before cutover.
      direction: "bidirectional",
      connectsToSystem: "cmc.contextMemoryCore",
      protocol: "internal_api",
      whatIsExchanged: [
      fromPort: "cmcIntegration",
      toSystem: "cmc.contextMemoryCore",
      type: "indexes_atoms",
      data_flow: "atoms \u2192 hierarchical_index",
      "direction": "bidirectional",
      "connectsToSystemId": "cmc.contextMemoryCore",
      "protocol": "internal_api",
      "data": ["atoms_for_indexing", "hierarchical_paths", "retrieval_queries"],

## AGENT-VIF (relevance: 0.40)
**AGENT-VIF** — VIF (Verifiable Intelligence Framework)
Domain: 23,871 tokens of context loaded
Relevance: 0.40

Relevant knowledge (20 lines):
      direction: "bidirectional",
      connectsToSystem: "cmc.contextMemoryCore",
      protocol: "internal_api",
      whatIsExchanged: [
      fromPort: "cmcIntegration",
      toSystem: "cmc.contextMemoryCore",
      type: "stores_witnesses",
      data_flow: "witnesses \u2192 persistent_storage",
      relationship: "CMC stores VIF witnesses and confidence scores persistently",
      whenToUse: "When implementing witness storage or understanding memory persistence",
      docs: [
        "systems/cmc/T2_architecture.md#vif-integration",
      "direction": "bidirectional",
      "connectsToSystemId": "cmc.contextMemoryCore",
      "protocol": "internal_api",
      "data": ["witness_storage", "confidence_scores", "verification_requests", "proof_artifacts"],

### CMC (Context Memory Core)
- **Purpose:** Store VIF witnesses as atoms in CMC
- **Integration:** `cmc_integration.py` - Witness storage and retrieval

## AGENT-SDFCVF (relevance: 0.40)
**AGENT-SDFCVF** — SDF-CVF (Atomic Evolution Framework)
Domain: 15,143 tokens of context loaded
Relevance: 0.40

Relevant knowledge (12 lines):
      direction: "bidirectional",
      connectsToSystem: "cmc.contextMemoryCore",
      protocol: "internal_api",
      whatIsExchanged: [
      fromPort: "cmcIntegration",
      toSystem: "cmc.contextMemoryCore",
      type: "validates_schema",
      data_flow: "atoms \u2192 consistency_checks",
      "direction": "bidirectional",
      "connectsToSystemId": "cmc.contextMemoryCore",
      "protocol": "internal_api",
      "data": ["evolution_artifacts", "trace_data", "change_history", "parity_results", "quartet_snapshots"],

## AGENT-APOE (relevance: 0.40)
**AGENT-APOE** — APOE (AI-Powered Orchestration Engine)
Domain: 23,602 tokens of context loaded
Relevance: 0.40

Relevant knowledge (53 lines):

- **PlanMemory** — In-memory representation of a single plan execution.
- **CMCPlanStore** — Stores and retrieves plan executions; optionally persists snapshots to CMC.
- **MemoryAwareExecutor** (4 methods)
- `_utc_now()`
- **PlanMemory** — Represents a stored plan execution in CMC.
- **CMCPlanStore** — Stores and retrieves plan executions from CMC.
- **MemoryAwareExecutor** (8 methods)
- **MemoryAwareExecutor** — Executor that stores execution history in CMC.
### `cmc_integration_v1.py` (238 lines)
- **PlanExecution** (2 methods)
- **APOECMC** — Clean v1 integration with simple in-memory cache + optional CMC client.
- **MemoryAwareExecutor** — Minimal executor facade to preserve test expectations while using APOECMC.
### `cmc_storage.py` (78 lines)
- **MockCMCClient** — Simple mock CMC client that captures create_atom payloads in-memory.
- **MockPlan** (1 methods)
- `_print_header()`
- **PlanMemoryV2** — In‑memory representation of a single plan execution (v2 sandbox).
- **PlanStatsV2** — Aggregated statistics for a given plan name.
- **CMCPlanStoreV2** — Isolated sandbox plan store for APOE→CMC v1/v2 integrations.
- **MemoryAwareExecutorV2** — Experimental executor that records plan execution snapshots via CMCPlanStoreV2.
- `_utc_now()` — Return current UTC time as a naive datetime.
- `test_get_plan_statistics_with_history()` — Test statistics calculation from history.
- `test_memory_aware_executor_stores_execution()` — Test that memory-aware executor stores execution.
- `test_should_retry_based_on_high_success_rate()` — Test retry recommendation with high success rate.
- `test_should_not_retry_based_on_low_success_rate()` — Test no retry recommendation with low success rate.
      direction: "bidirectional",
      connectsToSystem: "cmc.contextMemoryCore",
      protocol: "internal_api",
      whatIsExchanged: [

## AGENT-CAS (relevance: 0.40)
**AGENT-CAS** — CAS (Cognitive Analysis System)
Domain: 17,631 tokens of context loaded
Relevance: 0.40

Relevant knowledge (50 lines):
      direction: "bidirectional",
      connectsToSystem: "cmc.contextMemoryCore",
      protocol: "internal_api",
      whatIsExchanged: [
      fromPort: "cmcIntegration",
      toSystem: "cmc.contextMemoryCore",
      type: "stores_analysis_data",
      pattern: "store",
      relationship: "CAS stores decision logs and cognitive analysis in CMC",
      whenToUse: "When implementing cognitive storage or understanding memory persistence",
      docs: [
        "systems/cmc/T2_architecture.md#cas-integration",
      "direction": "bidirectional",
      "connectsToSystemId": "cmc.contextMemoryCore",
      "protocol": "internal_api",
      "data": ["cognitive_analyses", "decision_logs", "introspection_data", "learning_data"],
- **Document Activation**: Monitors which documents are currently being used
- **Context Awareness**: Tracks working memory items and context size
- **Load Monitoring**: Monitors cognitive load levels
- **Warning System**: Alerts when critical principles are cold but needed
# Classify a task
task_result = category_recognizer.classify_task("Update memory files")
print(f"Category: {task_result.detected_category}")
print(f"Required protocols: {task_result.required_protocols}")
failure = failure_analyzer.analyze_categorization_error(
    task_description="Update memory files",
    detected_category="routine_maintenance",
    confidence=0.2,
- `ROUTINE_HOUSEKEEPING`: Simple maintenance tasks
- `CRITICAL_MEMORY_MODIFICATION`: Memory system changes

## AGENT-TCS (relevance: 0.40)
**AGENT-TCS** — TCS (Timeline Context System)
Domain: 16,593 tokens of context loaded
Relevance: 0.40

Relevant knowledge (20 lines):

- **TimelineMemoryStore** — Lightweight adapter that persists timeline context using the CMC memory
- **ContextType** — Types of context being tracked
- **ConfidenceLevel** — Confidence levels for context tracking
      direction: "bidirectional",
      connectsToSystem: "cmc.contextMemoryCore",
      protocol: "internal_api",
      whatIsExchanged: [
      fromPort: "cmcIntegration",
      toSystem: "cmc.contextMemoryCore",
      type: "stores_timeline_data",
      data_flow: "timeline_data \u2192 persistent_storage",
      relationship: "TCS stores timeline nodes and consciousness journals in CMC",
      whenToUse: "When implementing timeline storage or understanding memory persistence",
      docs: [
        "systems/cmc/T2_architecture.md#tcs-integration",
      "direction": "bidirectional",
      "connectsToSystemId": "cmc.contextMemoryCore",
      "protocol": "internal_api",
      "data": ["timeline_nodes", "consciousness_journals", "context_snapshots", "summary_data"],

## AGENT-IIS (relevance: 0.40)
**AGENT-IIS** — IIS (Intuitive Intelligence System)
Domain: 6,773 tokens of context loaded
Relevance: 0.40

Relevant knowledge (18 lines):

IIS (Intuitive Intelligence System) enables genuine AI intuition through meta-pattern matching, 4D temporal-spatial reasoning, and recursive self-improvement. It transforms AI from pattern-matching to intuitive consciousness with meta-cognitive capabilities. IIS integrates with CMC for memory, HHNI for retrieval, VIF for verification, Timeline for context, and CAS for meta-analysis. Components include 4D Reasoning Engine, Intuitive Pattern Matcher, Meta-Intuition Tracker, and Evolution Predictor. This T-level doc reflects newest standards without modifying legacy L-level docs. See system maps and indices for relationships; use validation gate before cutover.
      direction: "bidirectional",
      connectsToSystem: "cmc.contextMemoryCore",
      protocol: "internal_api",
      whatIsExchanged: [
      fromPort: "cmcIntegration",
      toSystem: "cmc.contextMemoryCore",
      type: "stores_intuition_data",
      data_flow: "intuition_data \u2192 persistent_storage",
      relationship: "IIS stores intuition traces and learning data in CMC",
      whenToUse: "When implementing intuition storage or understanding memory persistence",
      docs: [
        "systems/cmc/T2_architecture.md#iis-integration",
      "direction": "bidirectional",
      "connectsToSystemId": "cmc.contextMemoryCore",
      "protocol": "internal_api",
      "data": ["intuition_traces", "learning_data", "calibration_data", "pattern_data"],

## Synthesized Answer
Based on input from 9 specialist agents (230,437 tokens collective context):


**AGENT-CMC** (relevance 0.90):

  Relevant knowledge (138 lines):
  title: "CMC Executive Summary"
  description: "100-word executive summary of Context Memory Core"
  audience: "executives, quick reference"
  confidence_threshold: 0.80
  status: "complete"
  tags: ["cmc", "core", "memory", "bitemporal", "t0-t6", "transitional"]
  dependencies: []
  related_docs: ["cmc_T1_overview", "system.map.lucid.json5"]
  # CMC (Context Memory Core) – T0 Executive Summary (≈100 words)

**AGENT-SEG** (relevance 0.40):

  Relevant knowledge (24 lines):
        direction: "bidirectional",
        connectsToSystem: "cmc.contextMemoryCore",
        protocol: "internal_api",
        whatIsExchanged: [
        fromPort: "cmcIntegration",
        toSystem: "cmc.contextMemoryCore",
        type: "provides_provenance_data",
        data_flow: "atoms \u2192 graph_nodes",
        relationship: "SEG stores graph nodes and provenance edges in CMC",

**AGENT-HHNI** (relevance 0.40):

  Relevant knowledge (20 lines):
  - **TagPriorityVector** (0 methods)
  - **HHNINode** — In-memory representation of a HHNI node prior to persistence.
  - `utc_now()`
  - `sha256_hex()`
  ### `test_memory_store_integration.py` (79 lines)
  - `tmp_store()`
  HHNI is the Hierarchical Hypergraph Neural Index that retrieves and organizes context using physics‑guided optimization. It builds a fractal hierarchy and uses DVNS forces to compress and de‑duplicate context under token budgets. HHNI integrates with CMC for bitemporal memory, VIF for verification, SEG for synthesis, and APOE for orchestration. This T‑level executive reflects the new documentation standards without changing legacy L‑level content. After review, it will replace the existing executive. See system maps and indices for relationships; run the validation gate before cutover.
        direction: "bidirectional",
        connectsToSystem: "cmc.contextMemoryCore",

**AGENT-VIF** (relevance 0.40):

  Relevant knowledge (20 lines):
        direction: "bidirectional",
        connectsToSystem: "cmc.contextMemoryCore",
        protocol: "internal_api",
        whatIsExchanged: [
        fromPort: "cmcIntegration",
        toSystem: "cmc.contextMemoryCore",
        type: "stores_witnesses",
        data_flow: "witnesses \u2192 persistent_storage",
        relationship: "CMC stores VIF witnesses and confidence scores persistently",

**AGENT-SDFCVF** (relevance 0.40):

  Relevant knowledge (12 lines):
        direction: "bidirectional",
        connectsToSystem: "cmc.contextMemoryCore",
        protocol: "internal_api",
        whatIsExchanged: [
        fromPort: "cmcIntegration",
        toSystem: "cmc.contextMemoryCore",
        type: "validates_schema",
        data_flow: "atoms \u2192 consistency_checks",
        "direction": "bidirectional",