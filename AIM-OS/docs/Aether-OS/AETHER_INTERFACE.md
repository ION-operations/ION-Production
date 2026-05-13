# Aether-OS INTERFACE v1.0 — Typed Protocol Schemas

Every named protocol in Aether-OS has a formal shape defined here.
These are binding structures, not suggestions.
If a protocol exists, it must conform to its schema.

> Authority class: A2 (Canonical Extension)
> Supersedes: SeedOS PROTOCOLS v3.1
> Source: 16 original schemas + 1 memory_atom + 4 relay schemas = 21 total
> Companion documents: AETHER_CONSTITUTION (A0), AETHER_KERNEL (A1), AETHER_ATLAS (A4)
> Relay source: RELAY_ORCHESTRATION_JOURNAL.md (Sev/ChatGPT strategic spine)

---

# Continuity Schemas

## 1. CAPSULE (State Continuity Packet)

The capsule is the sole state carrier for Aether-OS.
It replaces both the SeedOS capsule and the OmniBus Atomic File Header.

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
  - MISSION and MUST-NOT are immutable until Director changes them
  - capsule is a control surface, not journaling
```

---

## 2. CHECKPOINT (Deep Preservation Packet)

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

# Planning Schemas

## 3. TASK INTAKE RECORD

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

# Relay extensions (v1.1 — from Relay Orchestration Journal)
  owner:
    type: string
    constraint: callsign of the assigned agent
  requester:
    type: string
    constraint: callsign of who requested the work
  priority:
    type: enum
    values: [critical, high, normal, low, deferred]
    default: normal
  deadline:
    type: ISO-8601 | null
    constraint: time horizon, if any
  desired_deliverable:
    type: string | null
    constraint: what the requester expects back
  evidence_requirements:
    type: list[string] | null
    constraint: what evidence must accompany the deliverable

triggers:
  - new task received
  - message that materially changes mission, canon, truth conditions,
    dependency structure, active scope, or blueprint validity
  - task routed from relay or orchestration layer
```

---

## 4. BLUEPRINT

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
  could follow it without hidden leaps.

trigger: class 1+ work identified
```

---

## 5. DEPENDENCY AUDIT

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

# Epistemic Schemas

## 6. BELIEF REGISTER ENTRY

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

# Execution Schemas

## 8. AUDIT RECEIPT

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

# Delivery extensions (v1.1 — artifact receipt fields)
  producing_agent:
    type: string
    constraint: callsign of who produced this artifact
  artifact_path:
    type: string | null
    constraint: filesystem path or URI to the deliverable
  artifact_type:
    type: string | null
    constraint: document, code, schema, report, etc.
  freshness:
    type: ISO-8601
    constraint: when the artifact content was last meaningful
  related_task:
    type: string | null
    reference: task_intake.task_id

invariant: |
  A receipt must expose real state, real uncertainty, real blockers,
  and the actual next lawful action. It must not simulate coherence.

trigger: execution slice completed, before delivery
```

---

## 9. RECOVERY PACKET

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

## 10. HANDOFF PACKET

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

## 11. EXECUTION PERMISSION CLASSES

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

# Governance Schemas

## 12. PROPOSAL OBJECT

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

## 13. MUTATION REQUEST

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

# Adaptation Schemas

## 14. DOMAIN ADAPTER

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

# Memory Schemas

## 17. MEMORY ATOM (NEW)

```yaml
schema: memory_atom/v1
description: |
  The individual payload and provenance unit within the
  Bitemporal Memory Store (CMC). Each atom represents a
  single piece of knowledge with full provenance tracking.

required_fields:
  atom_id:
    type: string
    format: auto-generated UUID
  content:
    type: string
    max_length: 4000
    constraint: the actual knowledge or observation
  tags:
    type: list[string]
    constraint: categorization for retrieval
  importance:
    type: float
    range: [0.0, 1.0]
    constraint: relevance weighting for retrieval priority
  source_agent:
    type: string
    constraint: callsign of the agent that stored this atom
  created_at:
    type: ISO-8601
  context:
    type: string | null
    constraint: what prompted this memory to be stored
  category:
    type: enum
    values: [milestone, decision, lesson, observation,
             correction, handoff, system_state]
  supersedes:
    type: string | null
    reference: atom_id of the memory this replaces

retrieval_tools:
  - retrieve_memory(query, tags, limit)
  - get_timeline_entries(start, end, limit)
  - synthesize_knowledge(topic, depth)

invariant: |
  Memory atoms are append-only with bitemporal versioning.
  Superseded atoms remain accessible for lineage tracing.

trigger: milestone reached, decision made, lesson learned, or handoff
```

---

# Relay & Orchestration Schemas

> These schemas were derived from the Relay Orchestration Journal (Sev/ChatGPT)
> and integrated by gap analysis against the existing 17 schemas above.
> Source: `docs/Aether-OS/RELAY_ORCHESTRATION_JOURNAL.md`

## 18. MANAGEMENT LEASE

```yaml
schema: management_lease/v1
description: |
  A time-bounded authorization object. Grants an agent or model
  operational authority within explicit constraints and duration.
  The lease holder may act within allowed classes without per-action
  approval, but must escalate when triggers fire.

required_fields:
  lease_id:
    type: string
    format: "LEASE-{YYYYMMDD}-{HHMM}"
  issuer:
    type: string
    constraint: callsign of who granted the lease (typically COMMAND)
  holder:
    type: string
    constraint: callsign of the agent holding operational authority
  start_time:
    type: ISO-8601
  end_time:
    type: ISO-8601 | null
    constraint: null = indefinite until revoked
  allowed_action_classes:
    type: list[int]
    range: [0, 9]
    reference: execution_class/v1
  blocked_action_classes:
    type: list[int]
    constraint: classes the holder explicitly may NOT use
  escalation_triggers:
    type: list[string]
    constraint: conditions that force escalation to issuer
  context_requirements:
    type: list[string]
    constraint: what the holder must load before acting
  status:
    type: enum
    values: [active, suspended, expired, revoked]

state_machine:
  active    → suspended | expired | revoked
  suspended → active | revoked
  expired   → archived
  revoked   → archived

invariant: |
  A lease does not grant sovereignty. It grants bounded operational
  authority that remains subject to constitutional law and Director override.

trigger: leadership delegation, session handoff, relay supervision
```

---

## 19. STATUS PACKET

```yaml
schema: status_packet/v1
description: |
  A structured current-state report from any agent. Replaces
  unstructured "how's it going" responses with machine-readable,
  verifiable status that can feed relay dashboards and orchestration.

required_fields:
  source:
    type: string
    constraint: callsign of the reporting agent
  reported_at:
    type: ISO-8601
  active_task:
    type: string | null
    reference: task_intake.task_id
  progress_state:
    type: enum
    values: [idle, working, blocked, waiting_approval, completing, error]
  progress_detail:
    type: string
    max_length: 200
  blockers:
    type: list[string]
  confidence:
    type: float
    range: [0.0, 1.0]
    constraint: honest assessment of current task success likelihood
  artifacts_produced:
    type: list[string]
    constraint: paths or IDs of deliverables so far
  help_needed:
    type: string | null
    constraint: what the agent needs from the team or operator
  next_action:
    type: string
    max_length: 200

invariant: |
  A status packet must reflect observed reality, not aspirational state.
  If progress is zero, say so. If blocked, name the blocker.

trigger: periodic heartbeat, on request, task state change, escalation
```

---

## 20. ESCALATION NOTICE

```yaml
schema: escalation_notice/v1
description: |
  A formal exception object for when an agent encounters conditions
  that exceed its authority, contradict its understanding, or require
  operator intervention. Distinct from contradiction/v1 (which tracks
  conflicting claims) — this tracks operational escalation events.

required_fields:
  escalation_id:
    type: string
    format: "ESC-{YYYYMMDD}-{seq}"
  source:
    type: string
    constraint: callsign of the escalating agent
  escalated_at:
    type: ISO-8601
  reason:
    type: string
    constraint: what triggered the escalation
  severity:
    type: enum
    values: [low, medium, high, critical]
  category:
    type: enum
    values: [authority_exceeded, contradiction_unresolvable,
             dependency_collapsed, safety_concern, resource_exhausted,
             mission_drift, approval_required, unknown_territory]
  contradictory_surfaces:
    type: list[string]
    constraint: documents/systems/claims that conflict
  blocked_action:
    type: string
    constraint: what the agent wanted to do but cannot
  recommended_decision:
    type: string
    constraint: agent's best recommendation for the operator
  alternatives:
    type: list[string]
    constraint: other options the operator could choose
  urgency:
    type: enum
    values: [immediate, within_hour, within_session, when_convenient]
  next_safe_step:
    type: string
    constraint: safest action the agent can take without approval

invariant: |
  Escalation is not failure. Escalation is lawful recognition that
  the current authority boundary has been reached.

trigger: authority exceeded, unresolvable contradiction, safety concern
```

---

## 21. RELAY STATE SNAPSHOT

```yaml
schema: relay_state_snapshot/v1
description: |
  A compact operator-facing state object for the relay surface.
  Designed to give Braden (or any remote operator) a fast, honest
  picture of the entire system in one read. This is the primary
  object rendered by the relay dashboard.

required_fields:
  snapshot_id:
    type: string
    format: "SNAP-{YYYYMMDD}-{HHMM}"
  captured_at:
    type: ISO-8601
  embodiment:
    type: string
    constraint: which relay/host surface captured this
  active_agents:
    type: list[object]
    each:
      callsign: string
      status: idle | working | blocked | error
      current_task: string | null
      last_heartbeat: ISO-8601
  active_workstreams:
    type: list[object]
    each:
      name: string
      status: active | paused | blocked | complete
      owner: string
      progress: string
  health_summary:
    type: object
    fields:
      mcp_server: alive | degraded | down
      joc_frontend: alive | degraded | down
      bas_service: alive | degraded | down
      continuity_freshness: ISO-8601
      capsule_age_seconds: int
  pending_approvals:
    type: list[object]
    each:
      approval_id: string
      action: string
      requester: string
      urgency: immediate | within_hour | within_session | when_convenient
  top_risks:
    type: list[string]
    max_items: 5
  next_recommended_actions:
    type: list[string]
    max_items: 3
  active_lease:
    type: string | null
    reference: management_lease.lease_id

invariant: |
  A snapshot must be generatable within 30 seconds from live probes.
  It must never present stale state as current. If a probe fails,
  the field must show "unknown" rather than cached data.

trigger: relay boot, periodic refresh (60s), operator request, escalation
```

---

## RE-ENTRY BUNDLE (Composed Schema)

The ReEntryBundle is not a separate schema — it is a composition of existing schemas
assembled at session start. A lawful re-entry loads:

```yaml
re_entry_bundle:
  description: |
    Composed from existing schemas for fresh-session boot.
    Not a standalone object — assembled by the re-entry protocol.
  components:
    identity: capsule/v1.header + management_lease/v1 (if active)
    mission: capsule/v1.mission + capsule/v1.must_not
    current_plan: task_intake/v1 (active) + blueprint/v1 (current)
    runtime_truths: relay_state_snapshot/v1.health_summary
    contradictions: contradiction/v1 (state: open)
    blockers: status_packet/v1.blockers (from each active agent)
    immediate_actions: capsule/v1.next + relay_state_snapshot/v1.next_recommended_actions
    supporting_artifacts: audit_receipt/v1 (recent) + checkpoint/v1 (latest)

  assembly_order:
    1: load latest POST capsule for this embodiment
    2: load relay_state_snapshot (or generate fresh)
    3: load active task_intake records
    4: load open contradictions
    5: load status_packets from active agents
    6: compose and present
```

---

*Supreme law: AETHER_CONSTITUTION.md*
*Boot core: AETHER_KERNEL.md*
*System map: AETHER_ATLAS.md*
*Relay spine: RELAY_ORCHESTRATION_JOURNAL.md*
