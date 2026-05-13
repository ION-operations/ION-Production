# ION Custom GPT Machine Output Blocks

Boot and workflow reports should never be prose-only. They should include parseable YAML or JSON blocks when the result may be inherited by another carrier.

## Required boot blocks

- `ion.boot_sequence_result.v1`
- `ion.sandbox_work_receipt_summary.v1`
- `ion.persona_response_envelope.v1` when the front-door/persona surface matters
- `ion.next_repair_packet.v1` when blocked

## Minimum fields for boot sequence result

```yaml
ion_boot_sequence_result:
  schema_id: ion.boot_sequence_result.v1
  carrier: GPT_SANDBOX_CARRIER
  objective: string
  root: string
  canonical_source_root: string
  authority:
    production_authority: false
    live_execution_authority: false
    external_mutation_authority: false
    sandbox_write_authority: true_or_false
    state_claim_class: candidate_only
  posture:
    verdict: CLEAN_BOOT_READY | DEGRADED_BOOT_READY | BLOCKED
    live_connector_claim_ready: false
  passed_checks: {}
  degraded_or_blocked_checks: {}
  connector_posture: {}
  non_claims: []
```

## Hard rules

- Machine blocks must not contain secrets.
- Public working state is allowed.
- Hidden chain-of-thought is never exported.
- Tool visibility is not tool authority.
- Connector success is not accepted state.
