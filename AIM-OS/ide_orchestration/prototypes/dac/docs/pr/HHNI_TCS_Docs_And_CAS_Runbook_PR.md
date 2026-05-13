Title: HHNI/TCS: Document Indirect Integration via CMC + CAS Payload Assertions + Validation Runbook

Summary
- Document TCS → CMC → HHNI indirect integration pattern and indexing filters.
- Add CAS hook payload assertions in HHNI tests (content_preview, selected_ids, dvns_iterations).
- Add validation runbook for TCS→CMC→HHNI end‑to‑end check.

Scope
- Files:
  - knowledge_architecture/systems/timeline_context_system/T2_architecture.md (updated)
  - knowledge_architecture/systems/hhni/T2_architecture.md (updated)
  - knowledge_architecture/systems/hhni/T3_detailed.md (updated)
  - packages/hhni/tests/test_cas_hooks.py (updated: snapshot‑like assertions)
  - ide_orchestration/prototypes/dac/docs/agents/sev/HHNI_TCS_VALIDATION_RUNBOOK.md (new)
- Clarifies:
  - Indexing filter: modality == plan_execution (APOE) and modality == tcs_timeline (TCS)
  - Required tags: plan_name:* and status:* for plan executions
  - CAS Phase‑1 activation hooks and enriched fields

Notes
- Tests green locally (pytest).
- Chronos & Alex boards updated; awaiting Chronos ACK to execute runbook.

Links
- Chronos board: ide_orchestration/prototypes/dac/docs/agents/chronos/COORDINATION_BOARD.md
- Sev board: ide_orchestration/prototypes/dac/docs/agents/sev/COORDINATION_BOARD.md
- Alex spec: ide_orchestration/prototypes/dac/docs/agents/alex/APOE_CMC_PAYLOAD_SPEC_v1.md


