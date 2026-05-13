# Roundtable Minutes

**Topic:** Comms FS Test
**Question:** How does CMC store memories?
**Agents:** 4/12 contributed
**Collective Context:** ~230,437 tokens
**Duration:** 21ms

## AGENT-CMC (relevance: 0.63)
**AGENT-CMC** — CMC (Context Memory Core)
Domain: 17,277 tokens of context loaded
Relevance: 0.63

Relevant knowledge (142 lines):

CMC provides structured, bitemporal memory for AI consciousness. It stores information with both transaction time and valid time, enabling time‑travel queries and perfect provenance. CMC integrates with HHNI for retrieval, VIF for verification/witnesses, and SEG for knowledge synthesis, underpinning APOE orchestration and SDF‑CVF quality. This T‑level doc reflects the newest standards (templates, metadata, gates) without modifying legacy L‑level docs. After review, this will become the canonical executive summary. See system maps and indices for relationships and navigation; use the validation gate to confirm completeness before cutover.
- `_setup_logging()`
- `_get_store()`
- `_resolve_correlation_id()`
- `atoms_create()`
### `memory_store.py` (810 lines)
- **MemoryStore** — Deterministic memory store with optional SQLite backend.
- **_NoOpDGraphClient** — No-op DGraph client when server unavailable. Allows HHNI indexing to complete (Qdrant vectors only).
- `_utc_now_iso()`
### `memory_store_TAGGED.py` (679 lines)
- `_log_extra()`
### `store_io.py` (125 lines)
- **JournalCorruptionError** — Raised when a journal fails integrity checks.
### `store_io_TAGGED.py` (237 lines)
- `store_timeline_entry_for_seg()` — Store a TCS timeline entry in CMC and return atom_id for SEG ingestion.
- `create_test_timeline_entry_for_gate_evidence()` — Create a test timeline entry for Priority 1 gate evidence capture.
- `tmp_store()` — Create a temporary MemoryStore for testing.
- `mock_hhni_clients()` — Mock DGraph and Qdrant clients for HHNI testing.
- `test_e2e_atom_creation_and_retrieval()` — Test: Create atom → List atoms → Verify content
### `test_memory_store.py` (292 lines)
- `sqlite_store()`
- `jsonl_store()`
- `test_create_and_list_atom()`
- `test_snapshot_roundtrip()`
- `cmc_store()` — Create a temporary CMC store for testing
- `test_store_timeli

## AGENT-SEG (relevance: 0.27)
**AGENT-SEG** — SEG (Shared Evidence Graph)
Domain: 16,504 tokens of context loaded
Relevance: 0.27

Relevant knowledge (102 lines):

- `store_execution_trace()` — Store APOE execution trace as SEG evidence node.
- `get_plan_effectiveness()` — Get plan effectiveness score from SEG evidence.
- `link_trace_to_evidence()` — Link APOE execution trace to SEG evidence node.
- `_ensure_cas_enabled()`
- `store_failure_pattern()` — Store CAS failure pattern as SEG evidence node.
- `get_failure_patterns()` — Get CAS failure patterns from SEG evidence by failure type.
- `link_pattern_to_evidence()` — Link CAS failure pattern to SEG evidence node.
- `store_evidence_in_cmc()` — Store SEG evidence node in CMC as an atom.
- `retrieve_evidence_from_cmc()` — Retrieve SEG evidence node from CMC atom.
- `link_evidence_to_cmc()` — Link existing SEG evidence node to CMC atom.
- `test_store_execution_trace_basic()` — Test basic execution trace storage.
- `test_store_execution_trace_with_graph()` — Test execution trace storage with graph.
- `test_get_plan_effectiveness()` — Test getting plan effectiveness score.
- `test_link_trace_to_evidence()` — Test linking trace to evidence.
- `test_store_failure_pattern_basic()` — Test basic failure pattern storage.
- `test_store_failure_pattern_with_graph()` — Test failure pattern storage with graph.
- `test_get_failure_patterns()` — Test getting failure patterns by type.
- `test_link_pattern_to_evidence()` — Test linking pattern to evidence.
- `test_store_evidence_in_cmc_basic()` — Test basic evidence storage in CMC.
- `test_retrieve_evidence_from_cmc_basic()` — Test basic evidence retrieval from CMC.
- `test_link_evidence_to_cmc_basic()` — Test linking evidence to CMC atom.
- `test_detect_multiple_contradictions()` — Test detecting multiple contradictions.
- `test_contradiction_stored_in_graph()` — Test that detected contradictions are stored.
- `test_contradiction_includes_confidence()` — Test that contradiction includes relation confidence.
- `t

## AGENT-VIF (relevance: 0.27)
**AGENT-VIF** — VIF (Verifiable Intelligence Framework)
Domain: 23,871 tokens of context loaded
Relevance: 0.27

Relevant knowledge (65 lines):

- **VIFStore** — High-level API for storing and retrieving VIF witnesses via CMC
- `vif_to_atom_payload()` — Convert VIF witness to CMC AtomCreate payload
- `atom_to_vif()` — Convert CMC atom back to VIF witness
- `create_witness_and_store()` — Convenience: create VIF witness and store in CMC
### `confidence_bands.py` (277 lines)
- `extract_rs_lift_metrics()` — Extract RS-Lift metrics from HHNI RetrievalResult.
- `store_rs_lift_in_witness()` — Store RS-Lift metrics in VIF witness metadata.
- `calculate_rs_lift_statistics()` — Calculate RS-Lift statistics from VIF witnesses.
- `create_retrieval_witness()` — Create VIF witness for HHNI retrieval operation.
- `test_atom_to_vif_wrong_modality()` — Test error when atom is not witness modality
- `test_vif_store_initialization()` — Test VIFStore initialization
- `test_vif_store_store_witness()` — Test storing VIF witness in CMC
- `test_vif_store_get_witness()` — Test retrieving VIF witness from CMC
- `test_create_witness_and_store()` — Test convenience function for creating and storing
- `test_roundtrip_serialization()` — Test full roundtrip: VIF → atom payload → CMC → atom → VIF
- `test_witness_tags_for_querying()` — Test that payload includes useful tags for CMC queries
- `test_extract_rs_lift_metrics_with_precision()` — Test extracting RS-Lift metrics with precision_at_k
- `test_store_rs_lift_in_witness()` — Test storing RS-Lift metrics in VIF witness
- `test_calculate_rs_lift_statistics()` — Test calculating RS-Lift statistics from VIF witnesses
- `test_create_retrieval_witness()` — Test creating VIF witness for HHNI retrieval operation
          tag: "[CMC-STORAGE]",
          purpose: "Witnesses stored with CMC atoms for provenance",
          type: "required",
          bidirectional: true,
          purpose: "Gated operations stored in CMC with confidence metadata",
      

## AGENT-APOE (relevance: 0.27)
**AGENT-APOE** — APOE (AI-Powered Orchestration Engine)
Domain: 23,602 tokens of context loaded
Relevance: 0.27

Relevant knowledge (59 lines):
- **PlanMemory** — In-memory representation of a single plan execution.
- **CMCPlanStore** — Stores and retrieves plan executions; optionally persists snapshots to CMC.
- **MemoryAwareExecutor** (4 methods)
- `_utc_now()`

- **PlanMemory** — Represents a stored plan execution in CMC.
- **CMCPlanStore** — Stores and retrieves plan executions from CMC.
- **MemoryAwareExecutor** (8 methods)
- **MemoryAwareExecutor** — Executor that stores execution history in CMC.
### `cmc_integration_v1.py` (238 lines)
- **PLIxCMCIntegration** — Stores PLIx execution artifacts in CMC.
### `compensation_engine.py` (180 lines)
- **PlanStatsV2** — Aggregated statistics for a given plan name.
- **CMCPlanStoreV2** — Isolated sandbox plan store for APOE→CMC v1/v2 integrations.
- **MemoryAwareExecutorV2** — Experimental executor that records plan execution snapshots via CMCPlanStoreV2.
- `_utc_now()` — Return current UTC time as a naive datetime.
- **MockPlan** (0 methods)
- `test_store_plan_start()` — Test storing plan execution start.
- `test_update_plan_progress()` — Test updating plan execution progress.
- `test_store_plan_complete_success()` — Test storing successful plan completion.
- `test_store_plan_complete_failure()` — Test storing failed plan completion.
- `test_retrieve_plan_history()` — Test retrieving plan execution history.
- `test_retrieve_plan_history_with_limit()` — Test retrieving plan history with limit.
- `test_get_plan_statistics_with_history()` — Test statistics calculation from history.
- `test_memory_aware_executor_stores_execution()` — Test that memory-aware executor stores execution.
- `test_should_retry_based_on_high_success_rate()` — Test retry recommendation with high success rate.
- `test_should_not_retry_based_on_low_success_rate()` — Test no retry recommendation with low success rate.
- `test_recommendations_with_warn

## Synthesized Answer
Based on input from 4 specialist agents (230,437 tokens collective context):


**AGENT-CMC** (relevance 0.63):

  Relevant knowledge (142 lines):
  CMC provides structured, bitemporal memory for AI consciousness. It stores information with both transaction time and valid time, enabling time‑travel queries and perfect provenance. CMC integrates with HHNI for retrieval, VIF for verification/witnesses, and SEG for knowledge synthesis, underpinning APOE orchestration and SDF‑CVF quality. This T‑level doc reflects the newest standards (templates, metadata, gates) without modifying legacy L‑level docs. After review, this will become the canonical executive summary. See system maps and indices for relationships and navigation; use the validation gate to confirm completeness before cutover.
  - `_setup_logging()`
  - `_get_store()`
  - `_resolve_correlation_id()`
  - `atoms_create()`
  ### `memory_store.py` (810 lines)
  - **MemoryStore** — Deterministic memory store with optional SQLite backend.
  - **_NoOpDGraphClient** — No-op DGraph client when server unavailable. Allows HHNI indexing to complete (Qdrant vectors only).
  - `_utc_now_iso()`

**AGENT-SEG** (relevance 0.27):

  Relevant knowledge (102 lines):
  - `store_execution_trace()` — Store APOE execution trace as SEG evidence node.
  - `get_plan_effectiveness()` — Get plan effectiveness score from SEG evidence.
  - `link_trace_to_evidence()` — Link APOE execution trace to SEG evidence node.
  - `_ensure_cas_enabled()`
  - `store_failure_pattern()` — Store CAS failure pattern as SEG evidence node.
  - `get_failure_patterns()` — Get CAS failure patterns from SEG evidence by failure type.
  - `link_pattern_to_evidence()` — Link CAS failure pattern to SEG evidence node.
  - `store_evidence_in_cmc()` — Store SEG evidence node in CMC as an atom.
  - `retrieve_evidence_from_cmc()` — Retrieve SEG evidence node from CMC atom.

**AGENT-VIF** (relevance 0.27):

  Relevant knowledge (65 lines):
  - **VIFStore** — High-level API for storing and retrieving VIF witnesses via CMC
  - `vif_to_atom_payload()` — Convert VIF witness to CMC AtomCreate payload
  - `atom_to_vif()` — Convert CMC atom back to VIF witness
  - `create_witness_and_store()` — Convenience: create VIF witness and store in CMC
  ### `confidence_bands.py` (277 lines)
  - `extract_rs_lift_metrics()` — Extract RS-Lift metrics from HHNI RetrievalResult.
  - `store_rs_lift_in_witness()` — Store RS-Lift metrics in VIF witness metadata.
  - `calculate_rs_lift_statistics()` — Calculate RS-Lift statistics from VIF witnesses.
  - `create_retrieval_witness()` — Create VIF witness for HHNI retrieval operation.

**AGENT-APOE** (relevance 0.27):

  Relevant knowledge (59 lines):
  - **PlanMemory** — In-memory representation of a single plan execution.
  - **CMCPlanStore** — Stores and retrieves plan executions; optionally persists snapshots to CMC.
  - **MemoryAwareExecutor** (4 methods)
  - `_utc_now()`
  - **PlanMemory** — Represents a stored plan execution in CMC.
  - **CMCPlanStore** — Stores and retrieves plan executions from CMC.
  - **MemoryAwareExecutor** (8 methods)
  - **MemoryAwareExecutor** — Executor that stores execution history in CMC.
  ### `cmc_integration_v1.py` (238 lines)