# True Name Binding Template

```yaml
schema_id: ion.true_name_binding.v0_1
true_name: "<carrier>_<lane><sequence>_<mission_movement>"
parsed_true_name:
  carrier: "<carrier>"
  lane: "<A-Z>"
  sequence: 1
  mission_movement: "<mission_movement>"
  inferred_domain: "<domain>"
folder_domains:
  - "<domain>"
context_package_ids:
  - "<context package id>"
allowed_path_scopes:
  - "ION/<path>"
expected_receipts:
  - "ION/05_context/current/worker_shift/signons/<receipt>.json"
  - "ION/05_context/current/worker_shift/leases/<receipt>.json"
  - "ION/05_context/current/worker_shift/signoffs/<receipt>.json"
binding_status: ACTIVE
binding_ready: true
incomplete_reasons: []
authority:
  accepted_state_authority: false
  production_authority: false
  live_execution_authority: false
  secrets_authority: false
  deploy_authority: false
```
