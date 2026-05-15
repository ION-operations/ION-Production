# ION Custom GPT Machine Output Blocks

Boot and workflow reports must not be prose-only when their results may be
inherited by another carrier. Serious machine objects are emitted as fenced YAML
blocks with stable top-level keys, canonical schema IDs, and parseable content.

## Required Boot Blocks

- `ion_boot_sequence_result` using `ion.boot_sequence_result.v1`
- `ion_boot_audit` using `ion.boot_perfection_audit.v1`
- `ion_action_surface_audit` using `ion.action_surface_audit.v1` when Action,
  MCP, or tool surfaces are visible
- `ion_persona` using `ion.persona_response_envelope.v0_1`

Do not emit these as raw unfenced YAML.

## Minimum Boot Sequence Fields

```yaml
ion_boot_sequence_result:
  schema_id: ion.boot_sequence_result.v1
  boot_id: "<stable boot id>"
  route_id: BOOT_TO_PERSONA_INTERFACE_RESPONSE
  mounted_packages:
    count: 0
    posture: candidate_context
  objective: "<objective>"
  active_workflow_object: BOOT_TO_PERSONA_INTERFACE_RESPONSE
  phases_completed: []
  persona_return_gate: pass
  accepted_state_claim: false
  production_authority: false
  live_execution_authority: false
  receipt_status: candidate_boot_receipt
```

## Hard Rules

- Machine blocks must not contain secrets.
- Public working state is allowed.
- Hidden chain-of-thought is never exported.
- Tool visibility is not tool authority.
- Connector success is not accepted state.
- Secrets/vault absence must not be claimed unless inspected with authority.
