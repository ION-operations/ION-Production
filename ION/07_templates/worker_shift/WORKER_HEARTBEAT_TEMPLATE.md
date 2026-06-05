# Worker Heartbeat Template

```yaml
schema_id: ion.worker_shift.heartbeat.template.v0_1
worker_id: "<worker runtime id>"
status: ACTIVE
note: "<optional short progress note>"
authority:
  production_authority: false
  live_execution_authority: false
  accepted_state_claim: false
  secrets_authority: false
expected_receipt:
  folder: ION/05_context/current/worker_shift/heartbeats/
  board: ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json
```
