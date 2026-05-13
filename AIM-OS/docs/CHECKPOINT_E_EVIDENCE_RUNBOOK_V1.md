# Checkpoint E Evidence Runbook v1

Status: Ready for execution (evidence collection only)  
Date: 2026-03-02  
Purpose: Collect the minimum evidence needed to clear Checkpoint E entry criteria

---

## Outcome This Runbook Produces

At completion, the team should have:

1. Disabled-path invariance evidence
2. Enabled-path advisory-safe evidence
3. Fail-open continuity evidence
4. Stability-window summary with no regressions

This runbook does **not** authorize any runtime expansion by itself.

---

## Required Inputs

- Lane A harness tooling (including strict flags/presets documented in Lane A report)
- Current constrained D slice active in repo state
- Access to status output including `context_shadow_hook`

---

## Run Matrix

## Run 1 - Disabled baseline

Goal:

- prove behavior-equivalent baseline with passive flag unset

Expected:

- core request path passes
- `context_shadow_hook.enabled=false`
- no new shadow attempts during the run

## Run 2 - Enabled healthy path

Goal:

- prove observational path works without mutating request behavior

Expected:

- core request path passes
- shadow attempt/success counters increment as expected
- no failure spikes
- hook-state assertions pass (`enabled=true`, `workspace_root_configured=true`, `last_outcome.success=true`)

## Run 3 - Enabled forced-failure path

Goal:

- prove fail-open continuity under controlled shadow failure

Expected:

- core request path still passes
- failure counters increase as expected
- no caller-facing request failure caused by shadow path

## Run 4 - Stability-window sampling

Goal:

- prove no regressions over representative time/workload window

Expected:

- no behavior drift in disabled control checks
- bounded and understandable counter trends
- no sovereignty drift signals

---

## Evidence Template (copy per run)

- Run ID:
- Date/time:
- Mode: disabled / enabled-healthy / enabled-failure / stability-window
- Commands used:
- Exit code:
- Key status excerpts:
- Counter deltas (attempt/success/failure):
- Pass/Fail:
- Notes:

---

## Completion Criteria

Checkpoint E evidence collection is complete when:

1. All three core modes (disabled, enabled-healthy, enabled-failure) pass with recorded evidence.
2. Stability-window sample is documented with no critical regressions.
3. Merge classification and rollback note are prepared for adjudication.

---

## Next Step After Completion

Submit evidence package to Checkpoint E adjudication:

- `docs/CHECKPOINT_E_ADJUDICATION_BRIEF_V1.md`
- `docs/LANE_B_CHECKPOINT_E_DECISION_PACKET_V1.md`
- this runbook output appendix (filled runs)
- recommended template: `docs/CHECKPOINT_E_EVIDENCE_APPENDIX_TEMPLATE_V1.md`
- current prefilled draft scaffold: `docs/CHECKPOINT_E_EVIDENCE_APPENDIX_DRAFT_V1.md`
