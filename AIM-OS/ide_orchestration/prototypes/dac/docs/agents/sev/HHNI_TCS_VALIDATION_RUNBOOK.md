# HHNI ↔ TCS Indirect Integration Validation Runbook (v1)

## Scope
- Validate the indirect pattern: TCS → CMC (`modality="tcs_timeline"` + `hhni_index`) → HHNI Poller → HHNI Index → Retrieval.

## Preconditions
- HHNI poller available: `packages/hhni/cmc_poller.py`
- CAS env optional; not required for this validation
- CMC test client or MCP tool to create atoms

## Steps
1) Create a `tcs_timeline` atom in CMC
- Fields:
  - `modality`: `tcs_timeline`
  - `tags`: include `hhni_index: true`
  - `content.inline`: small timeline text

2) Start/run HHNI poller (single iteration)
- Configure handler:
  - allowlist includes `tcs_timeline`
  - `page_size=50`
  - DLQ path set
- Run `handler.run_once()` and capture count
- Expect: count ≥ 1

3) Verify HHNI nodes persisted
- Inspect DGraph upsert calls (in test/fake) or query storage if live
- Expect: document/paragraph/sentence nodes created; paths include `doc:<atom_id>`

4) Retrieve via HHNI
- Use `TwoStageRetriever` with `target_level=PARAGRAPH`
- Query contains a phrase from timeline content
- Expect: selected items include nodes referencing the timeline atom

5) Idempotency check
- Re-run `handler.run_once()`
- Expect: count == 0 (already indexed)

6) DLQ behavior
- Create malformed atom (e.g., missing `id` or invalid content)
- Expect: entry appended to DLQ and no crash

## Acceptance Criteria
- New `tcs_timeline` atom with `hhni_index` is indexed within one poll cycle
- Retrieval returns items linked to the new atom
- Second poll skips duplicates (idempotent)
- Malformed atoms logged to DLQ

## Notes
- This validates the v1 indirect pattern; future v2 may add temporal weighting APIs and tighter CAS linkage.


