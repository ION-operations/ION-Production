# Rollback Playbook

Use this checklist when a gate failure or telemetry incident requires restoring
the orchestration state to a safe checkpoint.

## 1. Detect & Classify
- ☐ Confirm gate failure / outage context (gate ID, failure reason, impacted tasks).
- ☐ Capture supporting evidence (logs, telemetry snapshots, CLI outputs).

## 2. Save Current State
- ☐ Run `python -m ide_orchestration.orchestrator.run --generate-dynamic --gate-context <ctx>.json` to document outstanding remediation tasks.
- ☐ Create safety checkpoint:
  ```bash
  python -m ide_orchestration.orchestrator.run \
    --save-checkpoint incident_pre_rollback \
    --completed-tasks <list>
  ```

## 3. Restore Prior Checkpoint
- ☐ List available checkpoints (`--list-checkpoints`).
- ☐ Restore selected checkpoint:
  ```bash
  python -m ide_orchestration.orchestrator.run \
    --load-checkpoint stable_state \
    --completed-tasks <current list>
  ```
- ☐ Record action in `ide_orchestration/telemetry/recovery_log.jsonl`.

## 4. Revalidate
- ☐ Rerun progress report and gate checks.
- ☐ Update SHARED_MESSAGE_BOARD with what was rolled back and why.
- ☐ Requeue remediation tasks via dynamic generator if necessary.
