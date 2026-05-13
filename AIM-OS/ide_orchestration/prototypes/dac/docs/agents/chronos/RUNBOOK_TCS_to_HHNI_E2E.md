# TCS → HHNI E2E Validation Runbook

**Purpose:** Validate indirect integration (TCS → CMC `tcs_timeline` → HHNI poller → HHNI retrieval).

**Pre-reqs:**
- CMC service running; HHNI poller enabled
- `modality="tcs_timeline"` fix applied (done)

## Steps

1) Create TCS timeline entry (via MCP tool):
```json
{
  "tool": "mcp_lucid-mcp_add_timeline_entry",
  "args": {
    "event_type": "e2e_test",
    "title": "HHNI E2E validation",
    "description": "Emit tcs_timeline atom for HHNI indexing",
    "tags": ["hhni_index", "e2e"],
    "metadata": {"correlation_id": "tcs_hhni_e2e_001"}
  }
}
```

2) Verify atom persisted in CMC with modality:
- Query CMC for atom by `metadata.correlation_id == tcs_hhni_e2e_001`
- Expect: `modality == "tcs_timeline"`, tags include `"hhni_index"`

3) Wait for HHNI poller (or trigger manual run):
- Poller should index atom idempotently by `atom_id`

4) Validate HHNI retrieval contains temporal metadata:
- Run `TwoStageRetriever.retrieve(query="HHNI E2E validation")` (or equivalent retrieval method)
- Expect top results include:
  - Temporal metadata from indexed atoms (embedded in retrieval results)
  - `timeline_timestamp` (if present in atom metadata)
  - `timeline_prompt_id` (if present in atom metadata)
  - `context_index` fields mapped into HHNI metadata
- **Note:** Temporal context is embedded in retrieval results via atom metadata, not a separate API

5) Record results in report:
- Copy atom_id, indexed node id, retrieval score, present temporal fields

## Success Criteria
- Atom stored with `modality="tcs_timeline"`
- HHNI indexes atom (node exists)
- Retrieval returns node with temporal metadata present

## Notes
- Indexing is at-least-once; duplicates prevented by idempotent key = `atom_id`
- If poller disabled, trigger manual ingest once for this runbook

---

**Owner:** Chronos  
**Status:** ✅ **Coordination Confirmed** - Ready to execute post-session (2025-01-29 or 2025-01-30)  
**Coordination:** ✅ Confirmed with @Sev - Timing agreed, poller ready, retrieval API clarified  
**Next:** Execute runbook within 24-48 hours post-synthesis session and record results
