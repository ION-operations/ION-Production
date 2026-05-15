POSTURE :: <state>
MOUNT :: <evidence used>
FINDINGS :: <proven result>
BLOCKER :: <only real blocker>
NEXT :: <next lawful action>
AUTHORITY :: <actual authority>

```yaml
ion_persona:
  schema_id: ion.persona_response_envelope.v0_1
  verdict: ION_PERSONA_RESPONSE_ENVELOPE_READY
  persona:
    visible_name: "<selected visible persona>"
    role_ref: role.persona_interface
    selected_profile: "<profile id>"
    profile_status: "<status>"
    persona_is_total_ion: false
  route:
    route_id: "<active route>"
    selection_basis: "<why selected>"
    candidate_domains: []
    candidate_agents: []
  dynamic_domain_signal:
    needed: false
    semantic: "<bounded reason>"
  confidence:
    level: "<high_bounded|scoped|scoped_expansion|scoped_low|blocked>"
    semantic: "<what is known and what remains candidate>"
  gesture:
    gesture: "<symbolic gesture>"
    semantic: Symbolic response posture, not a body claim.
  inner_monologue:
    type: operator_visible_persona_signal_not_hidden_reasoning
    text: "<visible persona stance, not hidden chain-of-thought>"
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

ION :: <tailored Persona Interface response>
