# APOE → CMC Test Checklist (v1)

Scope: plan_execution emission + helpers + indexability  
Owner: Alex (APOE)

## Emission
- emits `modality == "plan_execution"`
- tags include: `"apoe","plan","execution","plan_name:<name>","status:<...>"`
- legacy kwargs path produces identical shape

## Ordering
- history sorted by `started_at` desc, then `execution_id` desc
- equal timestamps produce deterministic order via `execution_id`

## Metrics/helpers
- `should_retry_based_on_history(..., 0.70)` threshold respected
- `get_plan_recommendations(..., 0.80)` threshold respected
- recommendations include `avg_duration_seconds`

## HHNI indexability
- index filter works with `modality == plan_execution`
- tag parser extracts `plan_name:*` and `status:*`

## Status handling
- supports success|failed|partial
- partial: allows missing `finished_at`

## Edge cases
- clock skew within ±5s doesn’t break order (secondary key applied)
- batch/backfill with same minute timestamps remains deterministic

## Sample fixtures
- success execution with full metrics
- failed execution with `failure_reason`
- partial execution (no `finished_at`)

## Acceptance criteria
- All tests pass locally
- Deterministic ordering verified across 100 randomized samples
- Emitted atoms validate against example payload in `APOE_CMC_PAYLOAD_SPEC_v1.md`


