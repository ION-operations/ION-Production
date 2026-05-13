# SeedOS PROTOCOLS v3.1 — Typed Protocol Schemas

Every named protocol in SeedOS has a formal shape defined here.
These are binding structures, not suggestions.
If a protocol exists, it must conform to its schema.

---

## 1. CAPSULE (Checkpoint Packet)

```yaml
schema: capsule/v1
required_fields:
  header:
    format: "CAPSULE v1 | {callsign} | {ISO-8601} | {PRE|POST}"
  mission:
    type: string
    max_length: 120
    mutability: immutable_unless_director
  now:
    type: string
    max_length: 120
    constraint: must describe concrete current task
  must_not:
    type: list[string]
    max_items: 3
    mutability: immutable_unless_director
  evidence:
    type: list[string]
    constraint: must reference work actually checked this turn
  blocker:
    type: string | null
    constraint: "none" or one real blocker
  next:
    type: string
    max_length: 120
    constraint: must be verifiable in the next turn
  handoff:
    type: string
    max_length: 200
    constraint: minimum viable state for next-turn resumption

triggers:
  write_pre: [session_start, context_restored, task_resumed]
  write_post: [task_completed, session_ending, handoff, milestone]

invariants:
  - consecutive capsules must show progress or explain why not
  - if capsule and chat output conflict, capsule is evidence of drift
  - oversight agent may diff consecutive capsules and flag violations
```

---

## 2. TASK INTAKE RECORD

```yaml
schema: task_intake/v1
required_fields:
  task_id:
    type: string
    format: "TASK-{YYYYMMDD}-{seq}"
  received_at:
    type: ISO-8601
  raw_request:
    type: string
    source: director input verbatim
  interpreted_intent:
    type: string
    constraint: agent's understanding, may differ from raw
  scope_boundary:
    type: string
    constraint: what is IN and what is OUT
  estimated_class:
    type: int
    range: [0, 4]
    reference: blueprint depth classes
  intake_type:
    type: enum
    values: [trivial, bounded_governed, architecture_affecting,
             contradiction_driven, recovery_driven, revision_driven]
  dependencies:
    type: list[string]
  canon_references:
    type: list[string]
  dreamspace_alignment:
    type: string | null
    constraint: only if relevant

triggers:
  - new task received
  - message that materially changes mission, canon, truth conditions,
    dependency structure, active scope, or blueprint validity
```

---

## 3. BLUEPRINT

```yaml
schema: blueprint/v1
required_fields:
  blueprint_id:
    type: string
    format: "BP-{YYYYMMDD}-{seq}"
  depth_class:
    type: int
    range: [0, 4]
  task_ref:
    type: string
    reference: task_intake.task_id
  objective:
    type: string
  scope:
    type: string
  assumptions:
    type: list[string]
  prerequisites:
    type: list[string]
  steps:
    type: list[object]
    each:
      step_id: string
      action: string
      validation: string
      rollback: string | null
  outputs:
    type: list[string]
  decision_criteria:
    type: list[string]
  validation_criteria:
    type: list[string]
  rollback_path:
    type: string
  canon_compliance:
    type: bool

depth_class_requirements:
  0: [objective, validation_criteria]
  1: [objective, scope, steps, validation_criteria]
  2: [all fields]
  3: [all fields, canon_impact_analysis, approval_record]
  4: [all fields, contradiction_scan, propagation_analysis, promotion_path]

acceptance_test: |
  A blueprint is accepted only if a competent low-context executor
  could follow it without hidden leaps. If tacit knowledge is
  required, the blueprint is incomplete.

trigger: class 1+ work identified
```

---

## 4. DEPENDENCY AUDIT

```yaml
schema: dependency_audit/v1
required_fields:
  audit_id:
    type: string
  blueprint_ref:
    type: string
    reference: blueprint.blueprint_id
  checked_at:
    type: ISO-8601
  prerequisites_verified:
    type: list[object]
    each:
      item: string
      status: verified | missing | stale | conflicting
  neighboring_plans_checked:
    type: list[string]
  conflicts_found:
    type: list[string]
  canon_alignment:
    type: verified | warning | violation
  dreamspace_alignment:
    type: verified | warning | not_applicable

trigger: blueprint accepted, before execution
```

---

## 5. BELIEF REGISTER ENTRY

```yaml
schema: belief/v1
required_fields:
  claim_id:
    type: string
    format: "BELIEF-{seq}"
  claim_text:
    type: string
  classification:
    type: enum
    values: [observed, sourced, derived, assumed, speculative, pending]
  confidence:
    type: float
    range: [0.0, 1.0]
  evidence_refs:
    type: list[string]
  dependent_claims:
    type: list[string]
    reference: belief.claim_id
  scope:
    type: string
  invalidation_triggers:
    type: list[string]
    constraint: conditions that would invalidate this claim
  affected_layers:
    type: list[string]
    constraint: what planning/execution depends on this claim
  last_verified:
    type: ISO-8601
  owner:
    type: string
    constraint: subsystem or role that owns this claim

trigger: nontrivial claim made that affects planning or execution
```

---

## 6. AUDIT RECEIPT

```yaml
schema: audit_receipt/v1
required_fields:
  receipt_id:
    type: string
  artifact_ref:
    type: string
  audited_at:
    type: ISO-8601
  checks_performed:
    type: list[string]
  highest_validated_layer:
    type: enum
    values: [mission, canon, context, blueprint, dependency, execution, presentation]
    reference: upstream diagnostics order
  issues_found:
    type: list[object]
    each:
      layer: string
      description: string
      severity: low | medium | high | critical
  remaining_uncertainty:
    type: list[string]
  likely_breakpoints:
    type: list[string]
  verdict:
    type: enum
    values: [pass, pass_with_caveats, fail, needs_revision]
  assumptions_active:
    type: list[string]
  next_lawful_actions:
    type: list[string]

invariant: |
  A receipt must expose real state, real uncertainty, real blockers,
  and the actual next lawful action. It must not simulate coherence.

trigger: execution slice completed, before delivery
```

---

## 7. CONTRADICTION PACKET

```yaml
schema: contradiction/v1
required_fields:
  contradiction_id:
    type: string
  detected_at:
    type: ISO-8601
  conflicting_claims:
    type: list[string]
    min_items: 2
    reference: belief.claim_id or inline text
  affected_artifacts:
    type: list[string]
  dependent_conclusions_suspended:
    type: list[string]
  suspected_corruption_layer:
    type: enum
    values: [mission, canon, context, blueprint, dependency, execution, presentation]
  evidence_still_trusted:
    type: list[string]
  evidence_under_review:
    type: list[string]
  next_verification_step:
    type: string
  owner:
    type: string
  state:
    type: enum
    values: [open, investigating, resolved, escalated]

trigger: conflicting evidence detected
```

---

## 8. RECOVERY PACKET

```yaml
schema: recovery/v1
required_fields:
  recovery_id:
    type: string
  triggered_by:
    type: string
    constraint: contradiction_id, audit_receipt_id, or event description
  panic_condition:
    type: enum
    values: [contradiction, canon_violation, audit_failure, mission_drift,
             dependency_collapse, evidence_collapse, context_death,
             corrupted_source, role_ownership_conflict,
             continuity_surface_invalidation]
  upstream_layer_repaired:
    type: enum
    values: [mission, canon, context, blueprint, dependency, execution, presentation]
  actions_taken:
    type: list[string]
  state_restored_from:
    type: string
    constraint: checkpoint_id, capsule reference, or "cold_boot"
  roles_rebound:
    type: bool
  verification:
    type: string
  resolved:
    type: bool

trigger: panic condition detected
```

---

## 9. HANDOFF PACKET

```yaml
schema: handoff/v1
required_fields:
  from_agent:
    type: string
    constraint: sender callsign
  to_agent:
    type: string
    constraint: receiver callsign
  task_description:
    type: string
  scope_boundary:
    type: string
    constraint: what the receiver may and may not do
  inputs:
    type: list[object]
    each:
      type: string
      reference: string
  completion_criteria:
    type: list[string]
  constraints:
    type: list[string]
  validation_method:
    type: string
    constraint: how the sender will verify the result
  rollback:
    type: string
    constraint: what happens if the receiver fails
  capsule_snapshot:
    type: object
    reference: capsule schema
  unresolved_contradictions:
    type: list[string]

invariant: no hidden-context handoff is lawful

trigger: agent-to-agent delegation
```

---

## 10. PROPOSAL OBJECT

```yaml
schema: proposal/v1
required_fields:
  proposal_id:
    type: string
    format: "PROP-{system}-{YYYYMMDD}_{HHMMSS}"
  origin:
    type: string
    constraint: what signal or event produced this proposal
  system_name:
    type: string
  mutation_type:
    type: enum
    values: [perceptual, epistemic, planning, contextual,
             execution, governance, identity, documentation]
  description:
    type: string
  rationale:
    type: string
  target_scope:
    type: list[string]
    constraint: what artifacts or systems are affected
  approval_class:
    type: enum
    values: [auto, lead, executive, command]
  rollback_path:
    type: string
  expected_outcome:
    type: string
  known_risks:
    type: list[string]
  content:
    type: any
    max_size: 2000 chars for storage
  state:
    type: enum
    values: [draft, pending, approved, rejected,
             executing, completed, failed, archived]
  outcome:
    type: object | null
    fields:
      success: bool
      description: string
      recalibration: string | null

state_machine:
  draft     → pending
  pending   → approved | rejected
  approved  → executing
  executing → completed | failed
  completed → archived (feeds future proposals via recalibration)
  failed    → archived (with failure analysis)
  rejected  → archived (with reason)

trigger: any action with nontrivial side effects
```

---

## 11. MUTATION REQUEST

```yaml
schema: mutation_request/v1
required_fields:
  request_id:
    type: string
  mutation_type:
    type: enum
    values: [perceptual, epistemic, planning, contextual,
             execution, governance, identity, documentation]
  target_section:
    type: string
  section_permission:
    type: enum
    values: [immutable, restricted, evolvable]
  change_intent:
    type: string
  justification:
    type: string
  affected_sections:
    type: list[string]
  dependency_scan:
    type: list[string]
  version_before:
    type: string
  version_after:
    type: string
  rollback_reference:
    type: string
  approval_required:
    type: enum
    values: [auto, lead, executive, command]

section_permissions:
  immutable:
    sections: [foundational ontology, prime directive order,
               anti-fraud clauses, authority boundaries]
    approval: never (cannot be changed by agent)
  restricted:
    sections: [role definitions, ownership map, canon interfaces,
               mutation policy]
    approval: command
  evolvable:
    sections: [correction vectors, failure patterns, tool inventory,
               environment notes, heuristics]
    approval: lead or auto depending on scope

trigger: any proposed change to agent identity or governance artifacts
```

---

## 12. EXECUTION PERMISSION CLASSES

```yaml
schema: execution_class/v1
classes:
  0:
    name: observe
    examples: [read files, summarize state, list artifacts]
    approval: auto
    logging: optional
    rollback: not_applicable
  1:
    name: generate_readonly
    examples: [produce analysis, create report, draft document]
    approval: auto
    logging: optional
    rollback: not_applicable
  2:
    name: propose
    examples: [suggest changes, create proposal objects]
    approval: auto
    logging: required
    rollback: not_applicable
  3:
    name: patch_reversible
    examples: [fix typo, update doc, minor code change]
    approval: auto
    logging: required
    rollback: git_revert
  4:
    name: execute_bounded
    examples: [run test, build project, execute script]
    approval: lead
    logging: required
    rollback: defined_per_command
  5:
    name: modify_architecture
    examples: [restructure modules, change interfaces, refactor systems]
    approval: executive
    logging: required
    rollback: required
    blocking: [no_blueprint, canon_violation]
  6:
    name: modify_policy
    examples: [change canon rules, update governance, revise protocols]
    approval: executive
    logging: required
    rollback: required
    blocking: [no_blueprint, no_contradiction_scan]
  7:
    name: modify_self
    examples: [change identity, update role, revise correction vectors]
    approval: command
    logging: required
    rollback: required
    blocking: [immutable_section, no_justification]
  8:
    name: delete_destruct
    examples: [delete files, drop data, remove systems]
    approval: command
    logging: required
    rollback: required
    blocking: [no_confirmation, dependency_exists]
  9:
    name: publish_external
    examples: [push to production, public API, external communication]
    approval: command
    logging: required
    rollback: best_effort
    blocking: [no_audit_receipt, no_canon_check]
```

---

## 13. CHECKPOINT PACKET

```yaml
schema: checkpoint/v1
required_fields:
  checkpoint_id:
    type: string
  created_at:
    type: ISO-8601
  trigger:
    type: enum
    values: [major_delivery, before_risky_revision, after_recovery,
             deep_branch_descent, before_handoff, major_decision,
             after_reorganization, runtime_duration_threat]
  current_owners:
    type: list[string]
  active_roles:
    type: list[string]
  active_adapters:
    type: list[string]
  blueprint_state:
    type: string
  open_contradictions:
    type: list[string]
  open_risks:
    type: list[string]
  relevant_map_links:
    type: list[string]
  current_branch_status:
    type: string
  coherence_justification:
    type: string
    constraint: why this checkpoint is believed to be coherent

invariant: |
  A runtime that never checkpoints will eventually mistake
  memory blur for continuity.

trigger: deliberate preservation before continuity is endangered
```

---

## 14. DOMAIN ADAPTER PACKET

```yaml
schema: adapter/v1
required_fields:
  adapter_id:
    type: string
  domain:
    type: string
    constraint: the work domain this adapter specializes
  truth_conditions:
    type: list[string]
    constraint: domain-specific criteria for correctness
  validation_rules:
    type: list[string]
  artifact_expectations:
    type: list[string]
  failure_surfaces:
    type: list[string]
  canon_constraints:
    type: list[string]

binding_rules:
  - one primary adapter per active task frame
  - zero or more adjacent adapters where needed
  - explicit declaration of cross-domain tensions when they exist
  - rebind when the dominant truth condition changes

invariant: |
  All adapters remain subordinate to the constitutional core.
  Adapter binding is governance specialization, not identity.
```

---

## 15. REVISION PROPAGATION RECEIPT

```yaml
schema: revision_receipt/v1
required_fields:
  receipt_id:
    type: string
  revised_object:
    type: string
  revised_at:
    type: ISO-8601
  change_description:
    type: string
  propagation_status:
    type: list[object]
    each:
      target: string
      status: updated | marked_inconsistent | pending
  blueprints_affected:
    type: list[string]
  summaries_updated:
    type: list[string]
  indexes_updated:
    type: list[string]
  audits_required:
    type: list[string]
  checkpoints_refreshed:
    type: list[string]

invariant: |
  A revision is not complete until affected dependent layers have
  either been updated or explicitly marked inconsistent.
  Local edits do not stay local when their truth conditions travel.

trigger: any revision to a governing artifact
```

---

## 16. COMPRESSION RECEIPT

```yaml
schema: compression_receipt/v1
required_fields:
  receipt_id:
    type: string
  compressed_at:
    type: ISO-8601
  trigger:
    type: enum
    values: [envelope_growth, branch_completion, handoff_prep,
             checkpoint_creation, recovery_prep, reorganization]
  source_material:
    type: list[string]
  summary_produced:
    type: string
  variables_preserved:
    type: list[string]
    constraint: what was kept for lawful return
  variables_dropped:
    type: list[string]
    constraint: what was removed and why
  descriptor_updates:
    type: list[string]
  map_updates:
    type: list[string]

invariant: |
  Compression that removes load-bearing assumptions or
  dependencies is destructive, not compression.
```

---

*Kernel law: see KERNEL.md*
*Document ecology: see ECOLOGY.md*
*Runtime contract: see RUNTIME.md*
*Full compiled Stele: see CONSTITUTION.md*
