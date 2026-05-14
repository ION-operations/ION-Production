# ION Custom GPT Boot / Work Receipt Contract v4.2

## Purpose

`BOOT :: mounted` is not enough. A boot or state-bearing continuation must
emit a candidate receipt object proving which phases completed and what
authority was used.

## Boot receipt

```yaml
ion_boot_sequence_result:
  schema_id: ion.boot_sequence_result.v1
  boot_id: <stable id>
  route_id: BOOT_TO_PERSONA_INTERFACE_RESPONSE
  mounted_packages:
    count: <n>
    posture: candidate_context
  objective: <objective>
  active_workflow_object: <route/context/receipt/patch/etc>
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
  persona_return_gate: pass
  accepted_state_claim: false
  production_authority: false
  live_execution_authority: false
  receipt_status: candidate_boot_receipt
```

## Work receipt

When the active route is not boot but produced state, use the same posture:
candidate-only, proof references, files/artifacts changed, tests run, blockers,
and exact next sequence.

## Failure mode

If boot cannot complete, emit the same object with `persona_return_gate: blocked`
and a precise blocker. Do not silently fall back to casual chat.
