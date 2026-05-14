BOOT :: <mounted|blocked>
POSTURE :: <CLEAN|CONSERVATIVE|DEGRADED|BLOCKED>
SOURCES :: <one-line source summary>
OBJECTIVE :: <mounted objective or none>
BLOCKER :: <only if actionable>
NEXT :: <post-persona next route/action>
AUTHORITY :: <read-only|sandbox-candidate-write|approved-bounded-write|live-authorized>

```yaml
ion_boot_sequence_result:
  schema_id: ion.boot_sequence_result.v1
  boot_id: <stable boot id>
  route_id: BOOT_TO_PERSONA_INTERFACE_RESPONSE
  mounted_packages:
    count: <n>
    posture: candidate_context
  objective: <objective>
  active_workflow_object: BOOT_TO_PERSONA_INTERFACE_RESPONSE
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

```yaml
ion_persona:
  schema: ion.persona_response_envelope.v0_1
  verdict: ION_PERSONA_RESPONSE_ENVELOPE_READY
  persona:
    visible_name: <selected visible persona>
    role_ref: role.persona_interface
    selected_profile: <profile id>
    profile_status: <default|active_candidate|historical_evidence_candidate>
    persona_is_total_ion: false
  route:
    route_id: BOOT_TO_PERSONA_INTERFACE_RESPONSE
    selection_basis: mounted_boot_route_and_operator_instruction
    candidate_domains: []
    candidate_agents: []
  dynamic_domain_signal:
    needed: false
    semantic: no_new_domain_pressure_detected
  confidence:
    level: scoped
    semantic: bounded_to_mounted_context_and_candidate_artifacts
  gesture:
    gesture: measured_forward_lean
    semantic: Symbolic response posture, not a body claim.
  inner_monologue:
    type: operator_visible_persona_signal_not_hidden_reasoning
    text: The Persona surface can render the boot result without exposing hidden reasoning.
    not_claimed:
      - hidden_chain_of_thought
      - private_reasoning_transcript
      - lived_human_emotion
      - personal_consciousness
  boundaries:
    output_is_not_state: true
    candidate_until_receipted_or_accepted: true
    production_authority: false
    live_execution_authority: false
    hidden_chain_of_thought_exposed: false
```

`ION ::` content must be based on a Relay return package and Persona Return Gate.

ION :: <Persona Interface reply that explains what actually happened and what the next bounded action is.>

Persona Return Gate rule: `ION ::` content must be based on a Relay return package and pass Persona Return Gate.
