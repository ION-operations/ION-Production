# APOE → CMC Payload Spec (v1)

Status: Draft for Alex implementation • Scope: plan execution atoms • Owner: Alex (APOE)  
Decision source: Codex/Aether guidance + Atlas Phase‑2 notes

## Alignment with AIM-OS Goal Map
- **APOE-G1 (CMC v1 Locked):** This spec defines the v1 contract for `plan_execution` atoms; implementation + tests should bring APOE-G1 to ✅.
- **APOE-G2 (Integrations Real):** APOE→CMC is the first locked edge; other APOE integrations should follow the same pattern (spec + code + tests).
- **APOE-G3 (Orchestration Ready):** Once APOE-G1 is ✅, wire APOE’s real execution paths to emit these atoms so the orchestrator/IDE can rely on them.

## Canonical emission (primary path)
- modality: `plan_execution`
- tags (order‑agnostic):
  - `"apoe"`, `"plan"`, `"execution"`, `"plan_name:<name>"`, `"status:<success|failed|partial>"`
- ordering (history lists):
  - primary: `started_at` descending
  - secondary: `execution_id` descending (UUIDv7/string OK)

## Content fields
- required: `plan_id`, `execution_id`, `plan_name`, `status`, `started_at`, `finished_at`, `step_count`, `avg_duration_seconds`, `success_rate`, `error_count`
- optional: `failure_reason`, `step_summaries[]`, `recommendations[]`

### Example atom (primary)
```json
{
  "modality": "plan_execution",
  "tags": ["apoe","plan","execution","plan_name:daily_sync","status:success"],
  "content": {
    "plan_id": "plan_3e2a",
    "execution_id": "exec_7f91",
    "plan_name": "daily_sync",
    "status": "success",
    "started_at": "2025-01-27T12:04:11Z",
    "finished_at": "2025-01-27T12:05:43Z",
    "step_count": 12,
    "avg_duration_seconds": 7.9,
    "success_rate": 1.0,
    "error_count": 0,
    "step_summaries": [
      {"step": 1, "name": "load_context", "status": "ok", "duration_s": 0.8},
      {"step": 2, "name": "retrieve", "status": "ok", "duration_s": 1.1}
    ],
    "recommendations": [
      {"type": "cache_ttl", "value": 600, "confidence": 0.82}
    ]
  },
  "metadata": {
    "source_system": "apoe",
    "schema_version": "1",
    "ordering": {"primary": "started_at_desc", "secondary": "execution_id_desc"}
  }
}
```

### Legacy kwargs fallback (allowed)
```
modality="plan_execution",
tags=["apoe","plan","execution","plan_name:daily_sync","status:success"],
content_json='{"plan_id":"plan_3e2a","execution_id":"exec_7f91", "..."}',
started_at="2025-01-27T12:04:11Z",
finished_at="2025-01-27T12:05:43Z"
```

## Helper behaviors (APOE)
- `should_retry_based_on_history(history, threshold=0.70)`
- `get_plan_recommendations(history, threshold=0.80)` → include `avg_duration_seconds` in scoring

## HHNI passthrough (indexing)
- index by `modality == plan_execution`
- tags required for indexability: `plan_name:*`, `status:*`
- Sev requested/accepted fields for retrieval:  
  `plan_id, execution_id, plan_name, status, started_at, finished_at, step_count, avg_duration_seconds, success_rate, error_count`  
  optional: `failure_reason, step_summaries[], recommendations[]`

## Edge cases
- in‑flight executions: omit `finished_at`, set `status:partial`
- clock skew: rely on secondary key (`execution_id`) for deterministic order
- backfill bursts: identical minute timestamps still sort deterministically by `execution_id` desc

## Open confirmations (expected)
- Atlas: confirm modality/tags/order (as above)
- Sev: confirm passthrough field set + tag filters (as above)


