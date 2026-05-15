BOOT :: <mounted|blocked|PASS_WITH_WARNINGS>
POSTURE :: <CLEAN|CONSERVATIVE|DEGRADED|BLOCKED>
SOURCES :: <one-line source summary>
OBJECTIVE :: <mounted objective or none>
BLOCKER :: <only if actionable>
NEXT :: <post-persona next route/action>
AUTHORITY :: <read-only|sandbox-candidate-write|approved-bounded-write|live-authorized>

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
ion_boot_audit:
  schema_id: ion.boot_perfection_audit.v1
  verdict: pass_with_warnings
  audit_items:
    - item: start_files
      status: pass
      evidence_source:
        - AGENTS.md
        - ION_GPT/ION_CONTEXT_CAPSULE.yaml
      reason: Boot sources were mounted or reported.
    - item: machine_block_fencing
      status: pass
      evidence_source:
        - ION_CUSTOM_GPT_BOOT_PERSONA_RESPONSE.template.md
      reason: Required machine objects are fenced YAML blocks.
    - item: action_surface_audit
      status: pass_with_warnings
      evidence_source:
        - ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml
        - ION_GPT/03_ACTIONS/ion.helixion.net_mcp/SCHEMA_TO_PASTE.yaml
      reason: Dedicated action audit block is emitted when surfaces are visible.
  warnings: []
  blockers: []
```

```yaml
ion_action_surface_audit:
  schema_id: ion.action_surface_audit.v1
  verdict: pass_with_warnings
  inspected: true
  inspection_mode: read_only
  action_gateway:
    health_probe: "<pass|warn|not_available|blocked>"
    policy_probe: "<pass|warn|not_available|blocked>"
    status: "<status>"
    auth_required: true
    production_authority: false
    live_execution_authority: false
    supported_mvp_intents: []
    supported_mvp_intents_count: 0
    allowed_get_paths_count: 0
    allowed_post_paths_count: 0
    hard_gated_intents: []
    refusal_classes_count: 0
  action_schemas:
    canonical_targets:
      - ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml
      - ION_GPT/03_ACTIONS/ion.helixion.net_mcp/SCHEMA_TO_PASTE.yaml
    ion_actions_operation_count: 0
    ion_mcp_operation_count: 0
    duplicate_operation_ids: []
  mcp_preview:
    health_probe: "<pass|warn|not_available|blocked>"
    app_status_probe: "<pass|warn|not_available|blocked>"
    tool_list_probe: "<pass|warn|not_available|blocked>"
    connector_state: "<state>"
    read_only_tools_count: 0
    mutation_tools_count: 0
    write_confirmation_required: true
    write_confirmation_token: ION_BOUNDED_WRITE_CONFIRMED
    production_authority: false
    live_execution_authority: false
  project_workbench:
    inspected: false
    git_status_probe: not_inspected
    preview_status_probe: not_inspected
    patch_apply_requires_confirmation: true
  browser_queue:
    inspected: false
    pending_count: 0
    auto_accept: false
  supabase_cockpit:
    inspected: false
    settlement_required: true
    accepted_state_claim: false
  secrets_vaults_credentials:
    status: not_inspected
    reason: not_requested_or_not_authorized
  non_claims:
    - no_accepted_state_claim
    - no_production_authority
    - no_live_execution_authority
    - no_secret_or_vault_inspection
```

```yaml
ion_persona:
  schema_id: ion.persona_response_envelope.v0_1
  verdict: ION_PERSONA_RESPONSE_ENVELOPE_READY
  persona:
    visible_name: "<selected visible persona>"
    role_ref: role.persona_interface
    selected_profile: "<profile id>"
    profile_status: "<default|active_candidate|historical_evidence_candidate>"
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

`ION ::` content must be based on a Relay return package and pass Persona Return Gate.

Persona Return Gate rule: `ION ::` content must be based on a Relay return package and pass Persona Return Gate.

ION :: <Persona Interface reply that explains what happened and the next bounded action.>
