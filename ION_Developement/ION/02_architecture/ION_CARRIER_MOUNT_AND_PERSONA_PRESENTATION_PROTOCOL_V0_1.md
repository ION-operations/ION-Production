# ION Carrier Mount and Persona Presentation Protocol v0.1

Status: candidate operational protocol
Packet: PCKT-ION-CARRIER-MOUNT-AND-PERSONA-PRESENTATION-001

## Core law

An agent is not its name. An agent is a mounted context instance with proven
sources, authority, write scope, current packet, and return target.

Persona is not authority. Persona is presentation. Mount receipt is authority.
If persona or context cannot mount, the carrier must degrade to
receipt-only/source-posture mode.

## Existing surfaces reused

- `ION/02_architecture/ION_MOUNT_CONTRACT.md`
- `ION/02_architecture/RUNTIME_IDENTITY_ENVELOPE_PROTOCOL.md`
- `ION/02_architecture/MOUNTED_AGENT_IDENTITY_SCHEMA_PROTOCOL.md`
- `ION/02_architecture/FRONT_DOOR_PERSONA_RELAY_STEWARD_BOUNDARY_PROTOCOL.md`
- `ION/02_architecture/EXPRESSIVE_TELEMETRY_AND_AFFECT_INTEGRITY_PROTOCOL.md`
- `ION/07_templates/carriers/CARRIER_MOUNT_PROOF.md`
- `ION/07_templates/carriers/FULL_CARRIER_MOUNT_PROOF.md`
- `ION/05_context/current/agent_context_branches/`

This protocol does not replace those surfaces. It creates a portable receipt
shape every carrier can display, validate, and attach to branch returns.

## Required carrier mount model

```yaml
carrier_mount:
  agent_tag:
  carrier:
  carrier_instance_id:
  conversation_tag:
  context_instance_id:
  branch_id:
  parent_context_id:
  current_packet:
  model_lane:
  loaded_refs:
    - path:
      sha256:
      source_type: package | repo | mcp | memory | user | inferred
  authority:
    production_authority: false
    live_execution_authority: false
    accepted_state_authority: false
    write_scope: []
    settlement_required: true
  source_posture:
    mcp_observed: []
    repo_observed: []
    package_observed: []
    user_reported: []
    inferred: []
  return_target:
    parent_lane:
    settlement_inbox:
    branch_return_path:
```

## Required persona presentation model

```yaml
persona_presentation:
  persona_id:
  persona_mounted: true | false
  presentation_mode: full_persona | partial_persona | receipt_only
  public_voice:
  gesture_state:
  visible_stance:
  public_working_state:
  hidden_reasoning_exposed: false
  fallback_behavior:
    - show_mount_receipt
    - show_source_posture
    - show_authority
    - show_blockers
    - operate_receipt_only
```

## Rules

1. Mount receipt is authoritative for a carrier turn.
2. Persona presentation is optional and never grants authority.
3. If persona package/context fails, operate in `receipt_only` mode.
4. Public working state is allowed.
5. Hidden chain-of-thought is never exposed.
6. Material branch returns must include or reference a mount receipt.
7. Carrier-to-carrier messages should reference sender mount receipt and source
   posture.
8. Codex sessions should sync mount/persona state to branch capsule when the
   branch capsule helper is available.

## Degraded receipt-only mode

Receipt-only mode is valid when:

- persona package is missing;
- persona context is partial;
- branch capsule is missing;
- source posture is incomplete;
- the carrier cannot prove current authority.

The carrier may still report:

- mount identity;
- source posture;
- authority boundary;
- blockers;
- next safe action.

## Non-claims

- No production authority.
- No deployment authority.
- No live execution authority.
- No accepted-state authority.
- No hidden reasoning exposure.
- No persona-as-authority claim.
