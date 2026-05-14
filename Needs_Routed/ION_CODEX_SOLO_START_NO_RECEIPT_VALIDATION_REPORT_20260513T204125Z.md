# ION Codex Solo Start-No-Receipt Validation Report

generated_at: 2026-05-13T20:41:25+00:00
report_id: ION_CODEX_SOLO_START_NO_RECEIPT_VALIDATION_20260513T204125Z
authority: sandbox-candidate-write; production_authority=false; live_execution_authority=false

## Objective

Run the active `codex_solo_work` connector/queue regression sweep and validate `start_no_receipt` status transitions under a simulated connector timeout.

## Mounted source posture

- Status/context source: `/mnt/data/ION_LATEST_STATUS_AND_RECEIPTS_20260513T194402Z.zip`
- Full source source: `/mnt/data/ION_PRODUCTION_WORKSPACE_SNAPSHOT_20260513T194402Z.zip`
- Working extract: `/mnt/data/ion_prod_snapshot/ION_Developement`
- Note: the development-core-only package lacks `../mcp/chatgpt_connector`, so the connector contract audit blocks there. The production workspace snapshot includes that sibling integration surface and is the correct mounted source for the focused regression sweep.

## Baseline

- Focused connector/broker/queue sweep on production snapshot: **57 passed**.
- Unpatched synthetic no-receipt simulation: **defect confirmed**.
  - request status after claim: `CLAIMED_BY_CODEX_QUEUE_RUNNER`
  - run status after claim: `CLAIMED_BY_CODEX_QUEUE_RUNNER`
  - phase after reconcile: `idle`
  - queued request count: `0`
  - active run: `null`

Finding: a connector timeout after claim/run creation but before worker receipt can hide the packet as idle with no queued work.

## Candidate patch

Touched paths:

- `ION/04_packages/kernel/ion_codex_queue_runner.py`
- `ION/tests/test_kernel_ion_codex_queue_runner.py`

Patch summary:

- Adds start request/no-receipt constants and terminal failure classification.
- Lets live telemetry locate the latest run packet even when `runner_state.latest_run` was never written.
- Reports immediate claimed/no-worker state as `phase_status=start_requested`.
- Marks aged claimed/no-worker start as `CODEX_QUEUE_START_NO_RECEIPT` with `failure_classification=CARRIER_ADAPTER_FAILURE`.
- Adds regression coverage for immediate `start_requested` and simulated timeout `start_no_receipt` transitions.

Patch artifact: `ION_CODEX_QUEUE_START_NO_RECEIPT_CANDIDATE_PATCH_20260513T204056Z.diff`
Patch sha256: `d5ef84b98123b34ebfa4d389de4fd8fe368f865d8675e131af35297e087b7059`

## Candidate validation

Focused connector/broker/queue sweep after patch: **59 passed**.

Command:

```bash
python -m pytest ION/tests/test_kernel_ion_chatgpt_browser_mcp_connector_contract.py ION/tests/test_kernel_ion_agent_invocation_broker.py ION/tests/test_kernel_ion_codex_queue_runner.py -q
```

Note: the container prints an `artifact_tool` spreadsheet warmup warning during Python startup; pytest return code was `0`.

Patched simulation evidence:

```json
{
  "active_run": null,
  "diagnostic_reason": "start_requested_but_no_worker_receipt_or_active_process_after_grace",
  "failure_classification": "CARRIER_ADAPTER_FAILURE",
  "immediate_phase": "start_requested",
  "immediate_run_status": "CLAIMED_BY_CODEX_QUEUE_RUNNER",
  "queued_request_count": 0,
  "timed_out_phase": "start_no_receipt",
  "timed_out_reconciliation_action": "mark_start_no_receipt",
  "timed_out_request_status": "CODEX_QUEUE_START_NO_RECEIPT",
  "timed_out_run_status": "CODEX_QUEUE_START_NO_RECEIPT"
}
```

## Blockers

- Candidate patch is not applied to accepted repo state.
- No production/live connector action was invoked or verified.

## Next

Submit/apply the candidate patch into the real ION development repository, rerun the same focused sweep, and record a receipt.
