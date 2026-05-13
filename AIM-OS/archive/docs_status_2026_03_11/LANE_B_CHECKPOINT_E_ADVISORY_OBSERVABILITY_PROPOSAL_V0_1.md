# Lane B Checkpoint E Advisory Observability Proposal v0.1

Status: Proposal only (no runtime mutation)  
Date: 2026-03-02  
Depends on: `docs/CHECKPOINT_E_ENTRY_CRITERIA_V1.md`

---

## Mission

Define the first **Checkpoint E** expansion slice as advisory observability only.

This proposal is explicitly:

- non-blocking
- non-governing
- evidence-producing
- rollback-simple

---

## Scope In

1. Add advisory signal definitions for shadow emission health and drift hints.
2. Define minimal payload shape for advisory records.
3. Define where advisories would be produced (conceptually) without changing routing.
4. Define report/validation requirements for any future implementation.

## Scope Out

- sync-state routing overrides
- contradiction enforcement in live path
- hard/soft gates
- daemon-plane governance coupling
- policy engines that mutate request behavior

---

## Proposed Advisory Signals (v0.1)

1. `shadow_emit_stale_warning`
   - trigger: no successful shadow emit in a configurable observation window
   - severity: `warn`

2. `shadow_emit_failure_rate_warning`
   - trigger: failure ratio exceeds threshold in recent window
   - severity: `warn` or `high` (advisory only)

3. `shadow_payload_shape_warning`
   - trigger: adapter/emitter payload incompatibility detected
   - severity: `warn`

4. `shadow_status_surface_inconsistency`
   - trigger: status counters or last outcome snapshot violate expected invariants
   - severity: `warn`

All signals are informational/advisory only in this slice.

---

## Minimal Advisory Record Shape (Draft)

```json
{
  "record_type": "bci_sync_advisory",
  "record_id": "uuid",
  "source_plane": "contextual_sync",
  "source_ref": "context_mapper.shadow_hook",
  "observed_at": "ISO-8601",
  "recorded_at": "ISO-8601",
  "sync_state": "stale|drift|unknown",
  "severity": "info|warn|high",
  "message": "human-readable advisory",
  "payload": {
    "signal_type": "string",
    "window_seconds": 0,
    "attempt_count": 0,
    "success_count": 0,
    "failure_count": 0
  },
  "provenance": {
    "producer": "checkpoint_e_advisory",
    "producer_version": "0.1.0"
  }
}
```

---

## Candidate Production Surface (Future, if authorized)

Preferred conceptual surface:

- post-observation aggregation path (not in live request critical path)
- derived from read-only status counters and shadow output telemetry

Avoid for first E slice:

- direct insertion into request routing decisions
- inline gating checks in envelope build path

---

## Validation Law (Future implementation)

Must prove:

1. advisory generation does not alter request success/failure outcomes
2. disabled/absence of advisory path leaves behavior unchanged
3. advisory records are schema-valid and queryable
4. rollback (disable path) is immediate and complete

---

## Merge Classification

- **Safe now**
  - this proposal doc
- **Safe later**
  - constrained advisory emission implementation after explicit Checkpoint E authorization
- **Not safe yet**
  - any behavior-affecting governance or gating

---

## Drift Check

- No live seam edits.
- Mapper/daemon/kernel sovereignty preserved.
- Contextual Sync remains additive superstrate.
