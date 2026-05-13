# Checkpoint E Evidence Appendix Template v1

Status: Template (fill-in)  
Date: 2026-03-02  
Use with: `docs/CHECKPOINT_E_EVIDENCE_RUNBOOK_V1.md`

---

## How To Use

1. Duplicate this file per evidence cycle (example: `CHECKPOINT_E_EVIDENCE_APPENDIX_YYYYMMDD.md`).
2. Fill every section with real command output summaries.
3. Keep pass/fail explicit and include exit codes.
4. Keep this factual; no policy decisions in this file.

---

## Cycle Metadata

- Evidence Cycle ID:
- Date Range:
- Operator:
- Environment/Branch:
- Target Build/Commit:
- Notes:

---

## Run 1 - Disabled Baseline

- Run ID:
- Timestamp:
- Commands:
- Exit Code:
- Expected Checks:
  - `context_shadow_hook.enabled=false`
  - no attempt/success increments
  - core request path passes
- Observed Results:
- Counter Snapshot (before):
- Counter Snapshot (after):
- Delta (attempt/success/failure):
- Pass/Fail:
- Evidence Excerpt:

---

## Run 2 - Enabled Healthy Path

- Run ID:
- Timestamp:
- Commands:
- Exit Code:
- Expected Checks:
  - core request path passes
  - attempt/success counters increment as expected
  - failure delta within allowed bound
- Observed Results:
- Counter Snapshot (before):
- Counter Snapshot (after):
- Delta (attempt/success/failure):
- Pass/Fail:
- Evidence Excerpt:

---

## Run 3 - Enabled Forced-Failure Path

- Run ID:
- Timestamp:
- Commands:
- Exit Code:
- Expected Checks:
  - request path still succeeds (fail-open)
  - failure counter increments
  - no governance/routing side effects
- Observed Results:
- Counter Snapshot (before):
- Counter Snapshot (after):
- Delta (attempt/success/failure):
- Pass/Fail:
- Evidence Excerpt:

---

## Run 4 - Stability Window Sampling

- Window ID:
- Start/End:
- Sampling Strategy:
- Commands/Automation Used:
- Exit Codes:
- Expected Checks:
  - no regressions in core paths
  - stable counter trends
  - no sovereignty drift signals
- Observed Results:
- Trend Notes:
- Incidents (if any):
- Pass/Fail:

---

## Consolidated Matrix

| Run | Mode | Exit Code | Pass/Fail | Key Finding |
|---|---|---:|---|---|
| 1 | Disabled baseline |  |  |  |
| 2 | Enabled healthy |  |  |  |
| 3 | Enabled forced-failure |  |  |  |
| 4 | Stability window |  |  |  |

---

## Merge Classification (for adjudication packet)

- Safe now:
- Safe later:
- Not safe yet:

---

## Rollback Note

- Immediate rollback action:
- Verification after rollback:

---

## Final Submission Checklist

- [ ] All runs documented with command + exit code
- [ ] Counter deltas captured where relevant
- [ ] Pass/fail explicit for each run
- [ ] Consolidated matrix completed
- [ ] Merge classification filled
- [ ] Rollback note filled
