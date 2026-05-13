# CMC → HHNI Notification Pattern

Date: 2025-01-27
Owner: Atlas (CMC)
Status: Proposed – ready for implementation
Priority: P1 (High)

---

## Goal
Enable automatic HHNI indexing when new/updated CMC atoms meet indexing criteria.

## Recommended Pattern (Event Journal + MCP Polling)

- Mechanism: Append-only event journal in CMC + HHNI polling via MCP tool
- Delivery: At-least-once (idempotent HHNI indexer)
- Simplicity: No cross-process callbacks needed; resilient to restarts

### Components
- CMC Event Journal: `packages/cmc_service/data/atoms.log` (JSONL) or SQLite `atoms` + `tags` tables
- MCP Tool (HHNI): `mcp_lucid-mcp_retrieve_memory` (to fetch new atoms by time/id)
- HHNI Indexer: Idempotent builder that indexes atoms by `atom_id`

### Trigger Rules (Atom filter)
- Modality allowlist: `{"text","tcs_timeline","plan_execution","cas_introspection_analysis","witness","evidence"}`
- Tag hints (any): `{"hhni_index","timeline_context","apoe","cas","vif","seg"}`
- Metadata gates: size < 1 MB inline; skip quarantine

### Polling Contract (HHNI)
- Cursor state: `{ last_atom_iso, last_atom_id }`
- Query window: `now - 60s … now`
- Page size: 200 atoms (configurable)
- Backoff: 2s when empty; 200ms when backlog detected

### Idempotency Contract
- HHNI maintains `indexed_atom_ids`
- If already indexed → skip
- If updated (same id, new created_at improbable) → re-index is safe

### Failure Handling
- On MCP/tool error: retry with exponential backoff (max 30s)
- On parse error: write to HHNI dead-letter queue with `atom_id`

## Minimal API (Pseudo)

- HHNI poller (pseudo):
```
while True:
  atoms = cmc.list_atoms(tag="hhni_index", limit=200, as_of_snapshot=None)
  for a in atoms:
    if not hhni.is_indexed(a.id):
      hhni.index(a)
  sleep(backoff)
```

- CMC helper (optional): `create_atom_with_hhni(payload, build_hhni=True)` already available; HHNI can also run standalone poller.

## Integration Points
- CMC side: No change required; ensure `tags` are stored and queryable (done)
- HHNI side: Implement poller + indexer entry (`build_hhni_for_atom`) – idempotent
- Router/Boards: Track progress in `HHNI_INTEGRATION_IMPLEMENTATION_PREP.md`

## Open Questions
1. Prioritization: Should HHNI prioritize `tcs_timeline` first? (recommended yes)
2. Snapshots: Use CMC snapshots as polling anchors? (optional v2)
3. Backfill: One-time full scan by tag = `hhni_index`

## Timeline
- v1 (today): Polling-based indexer (2-3h)
- v2: Snapshot-anchored polling (4-6h)
- v3: Event bus (optional, later)

## Acceptance Criteria
- New `tcs_timeline` atoms with `hhni_index` tag are indexed within 5s
- Idempotency verified with duplicate poll
- Dead-letter queue records malformed atoms without crashing indexer
