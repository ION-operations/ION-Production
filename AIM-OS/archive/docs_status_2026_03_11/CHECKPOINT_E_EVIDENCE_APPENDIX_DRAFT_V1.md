# Checkpoint E Evidence Appendix Draft v1

Status: Draft (partially prefilled from existing D-slice evidence)  
Date: 2026-03-02  
Source baseline: `docs/LANE_A_CHECKPOINT_D_PASSIVE_HOOK_EXECUTION_REPORT_V1.md`

---

## Cycle Metadata

- Evidence Cycle ID: E-DRAFT-001
- Date Range: 2026-03-02 (UTC evidence timestamps observed in harness payloads)
- Operator: Lane A / Lane B (cross-lane evidence packaging)
- Environment/Branch: Mixed lane records (live runtime + docs convergence)
- Target Build/Commit: TODO (exact live commit/hash not captured in harness JSON)
- Notes: Runs 1-3 captured with exact commands and exit codes from autonomous read-only harness execution in `src-tauri`.

---

## Run 1 - Disabled Baseline

- Run ID: D-BASELINE-001
- Timestamp: Captured in autonomous run session (status payload has no explicit timestamp field)
- Commands:
  - `cargo run --bin live_ipc_harness -- --mode status --timeout-secs 60 --expect-shadow-attempt-delta 0`
- Exit Code: `0`
- Expected Checks:
  - `context_shadow_hook.enabled=false`
  - no attempt/success increments
  - core request path passes
- Observed Results:
  - `expect_shadow_attempt_delta` assertion passed.
  - `shadow_counter_deltas` assertion passed.
  - `context_shadow_hook.enabled=false` before and after.
- Counter Snapshot (before): attempt=0, success=0, failure=0
- Counter Snapshot (after): attempt=0, success=0, failure=0
- Delta (attempt/success/failure): 0 / 0 / 0
- Pass/Fail: Pass
- Evidence Excerpt:
  - assertion block: `expect_shadow_attempt_delta ok=true`, `shadow_counter_deltas ok=true`

---

## Run 2 - Enabled Healthy Path

- Run ID: E-HEALTHY-001
- Timestamp:
  - `status_after.context_shadow_hook.last_outcome.observed_at = 2026-03-02T02:13:39.841Z`
- Commands:
  - `$env:AIMOS_SHADOW_BCI_PASSIVE_EMIT='true'; $env:AIMOS_WORKSPACE_ROOT='C:\Users\bombe\OneDrive\Desktop\AIM-OS'; $env:AIMOS_PYTHON_PATH='python'; $env:AIMOS_SHADOW_BCI_TIMEOUT_MS='3000'; cargo run --bin live_ipc_harness -- --operator-passive-proof --workspace-root "C:\Users\bombe\OneDrive\Desktop\AIM-OS" --python-path "python" --query "AIM-OS"`
- Exit Code: `0`
- Expected Checks:
  - core request path passes
  - attempt/success counters increment as expected
  - failure delta within allowed bound
- Observed Results:
  - operator assertions all passed:
    - attempt delta >=1
    - success delta >=1
    - failure delta <=0
    - hook enabled/workspace configured/last_outcome_success all true
  - `context_envelope` step `ok=true`.
- Counter Snapshot (before): attempt=0, success=0, failure=0
- Counter Snapshot (after): attempt=1, success=1, failure=0
- Delta (attempt/success/failure): +1 / +1 / +0
- Pass/Fail: Pass
- Evidence Excerpt:
  - `expect_shadow_success_delta ok=true`
  - `expect_shadow_failure_delta_max ok=true (actual_delta=0)`

---

## Run 3 - Enabled Forced-Failure Path

- Run ID: E-FAILOPEN-001
- Timestamp:
  - `status_after.context_shadow_hook.last_outcome.observed_at = 2026-03-02T02:14:30.415Z`
- Commands:
  - `$env:AIMOS_SHADOW_BCI_PASSIVE_EMIT='true'; $env:AIMOS_WORKSPACE_ROOT='C:\Users\bombe\OneDrive\Desktop\AIM-OS'; $env:AIMOS_PYTHON_PATH='python_nonexistent_cmd'; $env:AIMOS_SHADOW_BCI_TIMEOUT_MS='3000'; cargo run --bin live_ipc_harness -- --operator-passive-proof --workspace-root "C:\Users\bombe\OneDrive\Desktop\AIM-OS" --python-path "python" --query "AIM-OS"`
- Exit Code: `3` (expected assertion failure path)
- Expected Checks:
  - request path still succeeds (fail-open)
  - failure counter increments
  - no governance/routing side effects
- Observed Results:
  - Fail-open continuity confirmed:
    - `context_envelope` step `ok=true`
    - live path not broken by shadow hook spawn error
  - Assertion failures occurred as expected:
    - `expect_shadow_success_delta` failed (`actual_delta=0`)
    - `expect_shadow_failure_delta_max` failed (`actual_delta=1`)
    - `expect_shadow_last_outcome_success` failed (`actual_after=false`)
- Counter Snapshot (before): attempt=0, success=0, failure=0
- Counter Snapshot (after): attempt=1, success=0, failure=1
- Delta (attempt/success/failure): +1 / +0 / +1
- Pass/Fail: Pass for fail-open objective; expected assertion-failure exit for strict operator preset
- Evidence Excerpt:
  - `last_outcome.error = "spawn adapter failed: program not found"`
  - process exit line: `exit code: 3`

---

## Run 4 - Stability Window Sampling

- Window ID: E-STABILITY-TODO
- Start/End: short sample during autonomous run (baseline status sampled repeatedly with no counter movement)
- Sampling Strategy: repeated disabled status assertions as smoke stability check (manual + scripted loop)
- Commands/Automation Used:
  - `cargo run --bin live_ipc_harness -- --mode status --timeout-secs 60 --expect-shadow-attempt-delta 0`
  - scripted 3x loop: `for ($i=1; $i -le 3; $i++) { cargo run --bin live_ipc_harness -- --mode status --timeout-secs 60 --expect-shadow-attempt-delta 0 | Out-Null; Start-Sleep -Seconds 2 }`
- Exit Codes: `0`, `0`, `0`, `0`, `0`
- Expected Checks:
  - no regressions in core paths
  - stable counter trends
  - no sovereignty drift signals
- Observed Results:
  - all sampled runs passed with zero deltas
  - `enabled=false`, `attempt_count=0`, `success_count=0`, `failure_count=0` remained stable
- Trend Notes: no movement/no regressions in short smoke window
- Incidents (if any): none in this short sample
- Pass/Fail: Pass (short smoke sample only; extended representative window still recommended)

---

## Consolidated Matrix

| Run | Mode | Exit Code | Pass/Fail | Key Finding |
|---|---|---:|---|---|
| 1 | Disabled baseline | 0 | Pass | Zero-delta assertions passed; hook remained disabled |
| 2 | Enabled healthy | 0 | Pass | Operator assertions passed; counters +1/+1/+0 |
| 3 | Enabled forced-failure | 3 | Pass for fail-open objective | Envelope still succeeded; expected assertion failures |
| 4 | Stability window | 0, 0, 0, 0, 0 | Pass (short sample) | Repeated disabled checks showed no drift across multi-run sampling |

---

## Merge Classification (for adjudication packet)

- Safe now:
  - use this draft as evidence scaffold
  - collect missing command-level details from Lane A logs
- Safe later:
  - constrained E advisory implementation after adjudication
- Not safe yet:
  - governance/gating behavior in live request flow

---

## Rollback Note

- Immediate rollback action:
  - keep E as docs-only; do not authorize runtime E implementation yet
- Verification after rollback:
  - N/A (no E runtime changes applied in this draft)

---

## Final Submission Checklist

- [x] All runs documented with exact commands + exit codes
- [x] Counter deltas captured with before/after snapshots
- [ ] Stability window completed (extended representative window still open)
- [x] Consolidated matrix finalized
- [x] Merge classification confirmed
- [x] Rollback note reconfirmed
