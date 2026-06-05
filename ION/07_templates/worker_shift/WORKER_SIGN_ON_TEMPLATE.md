# Worker Sign-On Template

```yaml
schema_id: ion.worker_shift.sign_on.template.v0_1
worker_id: "<worker runtime id>"
carrier: "codex_cli | chatgpt_browser | capsule_agent | branch_agent"
mission: "<bounded mission or packet objective>"
allowed_paths:
  - "ION/<path>"
authority:
  production_authority: false
  live_execution_authority: false
  accepted_state_claim: false
  secrets_authority: false
expected_receipt:
  folder: ION/05_context/current/worker_shift/signons/
  board: ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json
```
