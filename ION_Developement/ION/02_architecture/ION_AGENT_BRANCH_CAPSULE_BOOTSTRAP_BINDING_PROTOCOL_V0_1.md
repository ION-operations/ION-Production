# ION Agent Branch Capsule Bootstrap Binding Protocol v0.1

Status: candidate consolidated protocol
Packet: PCKT-ION-BRANCH-CAPSULE-CONSOLIDATION-006

## Purpose

Bind Codex and other local agents to explicit branch identity at session start
without rewriting shared Capsule, Mini, HOT_CONTEXT, STATUS, or ROUTE files as
accepted state.

## Boot law

- Boot may surface branch-capsule law and helper references.
- Boot must be read-only and fail-soft.
- Boot must not assign C-numbers, checkpoints, or accepted-state status.
- Boot must not silently promote a branch return into shared context.
- A missing branch capsule is a warning for material work, not a reason to
  mutate shared context.

## Required branch identity

Each material agent session must carry:

- `context_instance_id`
- `branch_id`
- `agent_tag`
- `conversation_tag`
- `parent_context_id`
- `loaded_refs`
- `write_scope`
- `settlement_required`
- `accepted_state_authority: false`

## Codex binding

Codex startup should expose these references in the route surface:

- `ION/02_architecture/ION_AGENT_BRANCH_CAPSULE_PROTOCOL_V0_1.md`
- `ION/02_architecture/ION_AGENT_BRANCH_CAPSULE_BOOTSTRAP_BINDING_PROTOCOL_V0_1.md`
- `ION/02_architecture/ION_AGENT_BRANCH_CAPSULE_MATERIAL_WORK_GUARD_PROTOCOL_V0_1.md`
- `ION/02_architecture/ION_AGENT_BRANCH_CAPSULE_SETTLEMENT_INTAKE_PROTOCOL_V0_1.md`
- `ION/02_architecture/ION_AGENT_BRANCH_CAPSULE_REGISTRY_RECONCILIATION_PROTOCOL_V0_1.md`
- `ION/04_packages/kernel/ion_agent_branch_capsule.py`

## Non-claims

- No production authority.
- No deployment authority.
- No accepted-state authority.
- No shared context write authority.
- No queue worker authority.
