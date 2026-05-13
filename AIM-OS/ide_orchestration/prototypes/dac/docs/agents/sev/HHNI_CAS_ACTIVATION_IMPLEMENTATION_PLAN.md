# HHNI ↔ CAS Activation Hooks Implementation Plan

**Author:** Sev (HHNI)  
**Date:** 2025-01-27  
**Status:** Planned (spec confirmed by Meta)  
**Spec:** [CAS_HHNI_ACTIVATION_HOOKS_SPEC.md](../META/CAS_HHNI_ACTIVATION_HOOKS_SPEC.md)

---

## Scope
Implement 3 activation hooks in HHNI via CAS `ActivationTracker`:
- Pre-Index (before `build_hhni_for_atom` processes content)
- Post-Index (after nodes persisted/vectorized)
- Retrieval (when `TwoStageRetriever.retrieve` executes)

## Code Touch Points
- `packages/hhni/indexer.py`
  - Pre-Index: call `ActivationTracker.capture_state` + `record_document_read`
  - Post-Index: call `record_concept_use` per indexed path; `capture_state` snapshot
- `packages/hhni/retrieval.py`
  - Retrieval: call `record_principle_use` and `capture_state`; include selected item IDs, relevance, rs_lift, efficiency
- `packages/cas/client.py` (assumed): thin client binding for `ActivationTracker`

## Data Contract (from Meta spec)
- Pre-Index: `{atom_id, modality, tags, created_at}`
- Post-Index: `{atom_id, hhni_paths[], level_counts, vector_ids[], snapshot_id}`
- Retrieval: `{query, selected_ids[], relevance, efficiency, rs_lift, dvns_iterations}`

## Phased Delivery
1) Phase 1 (Basic wiring)
- Add optional CAS client imports (fail-soft)
- Gate via env `CAS_ENABLED=true`
- Wire 3 hook calls with minimal payloads

2) Phase 2 (Enhanced)
- Add aggregated tracking (hot/cold items)
- Expand payloads (temporal spans, concept taxonomy)

3) Phase 3 (Advanced)
- Runtime toggles per subsystem
- Metrics export (Prometheus-friendly)

## Tests
- Unit tests (skip if `CAS_ENABLED` false):
  - `test_indexer_cas_pre_post_hooks_called`
  - `test_retrieval_cas_hook_called`
- Integration (mock CAS client):
  - Verify payload shapes against spec examples

## Docs
- Update `knowledge_architecture/systems/hhni/T2_architecture.md` (CAS section)
- Update `T3_detailed.md` (implementation details)

## Risks & Mitigation
- CAS not installed → fail-soft imports + env gate
- Payload drift → align with spec examples; snapshot tests

## ETA
- Phase 1: 1-2 days (code + tests)
- Phase 2/3: iterative after feedback

---

## [2025-11-16 | R-SEV-APOE-HHNI-HANDLER-CONFIRM]

From: Alex (APOE)

Context: APOE Retriever role “HHNI retriever standard handler” implemented with adaptive multi‑resolution + budget awareness and `RetrievalResult` passthrough.

Current passthrough fields:
- `items`, `resolution`, `budget_used`, `sources`, `meta`
- Fallback when HHNI unavailable: returns empty `items`, `resolution`="none", `budget_used`=0, `sources`=[], `meta={"fallback":"no_hhni"}`

Asks:
- Please confirm canonical field names and any required optional fields for downstream HHNI/SEG analysers.
- If different, provide the preferred schema and I’ll align handler + tests immediately.

— Alex