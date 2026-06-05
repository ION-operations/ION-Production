# Work Lease Template

```yaml
schema_id: ion.worker_shift.work_lease.template.v0_1
worker_id: "<worker runtime id>"
lease_id: "<stable lease id>"
mode: "read | write | exclusive_write"
paths:
  - "ION/<path>"
objective: "<bounded reason for the claim>"
conflict_rule:
  exclusive_write: "blocks any overlapping read, write, or exclusive_write lease"
  write: "blocks only on overlapping active exclusive_write"
  read: "coexists with read"
authority:
  production_authority: false
  live_execution_authority: false
  accepted_state_claim: false
  secrets_authority: false
expected_receipt:
  folder: ION/05_context/current/worker_shift/leases/
  board: ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json
```
