# Worker Sign-Off Template

```yaml
schema_id: ion.worker_shift.sign_off.template.v0_1
worker_id: "<worker runtime id>"
summary: "<what changed or what was validated>"
touched_paths:
  - "ION/<path>"
validation:
  - "<command or proof result>"
next_baton: "<optional handoff note>"
authority:
  production_authority: false
  live_execution_authority: false
  accepted_state_claim: false
  secrets_authority: false
expected_receipt:
  folder: ION/05_context/current/worker_shift/signoffs/
  board: ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json
```
