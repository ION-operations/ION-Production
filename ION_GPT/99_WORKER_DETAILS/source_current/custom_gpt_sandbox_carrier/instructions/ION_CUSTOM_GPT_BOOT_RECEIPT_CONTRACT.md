# ION Custom GPT Boot Receipt Contract v0.4.2

Status: sandbox-candidate product contract.

For `boot-sequence`, compact telemetry is not enough. The carrier must emit a candidate boot receipt block before the Persona visible envelope.

Required block:

```yaml
ion_boot_sequence_result:
  schema_id: ion.boot_sequence_result.v1
  boot_id: <stable id>
  route_id: BOOT_TO_PERSONA_INTERFACE_RESPONSE
  mounted_packages:
    count: <n>
    posture: candidate_context
  objective: <objective>
  active_workflow_object: <route/context/receipt/etc>
  phases_completed:
    - PERSONA_INTERFACE_INGRESS
    - RELAY
    - STEWARD
    - VIZIER
    - MASON
    - NEMESIS_OR_VICE_REVIEW
    - SCRIBE
    - STEWARD_FINAL
    - RELAY_RETURN_PACKAGE
    - PERSONA_RETURN_GATE
    - PERSONA_INTERFACE_RESPONSE
  persona_return_gate: pass | blocked
  accepted_state_claim: false
  production_authority: false
  live_execution_authority: false
  receipt_status: candidate_boot_receipt
```

If blocked, name the precise blocker and emit a continuation envelope through `ION ::`.
