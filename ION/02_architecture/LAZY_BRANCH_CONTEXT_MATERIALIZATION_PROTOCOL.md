---
type: architecture_protocol
authority: A3_CANDIDATE
created: 2026-05-15T00:00:00-04:00
status: CANDIDATE
protocol_id: lazy_branch_context_materialization_protocol
purpose: Define how ION creates or inherits branch-local context only when real work enters a meaningful folder.
connections:
  - ION/02_architecture/README_BRANCH_CONTEXT_PROTOCOL.md
  - ION/02_architecture/ION_AGENT_CONTEXT_DYNAMICS_AND_CONTEXT_WINDOW_PROTOCOL.md
  - ION/02_architecture/ION_AGENT_CONTEXT_CONTINUITY_TIMELINE_AND_ROUTE_MAP_PROTOCOL.md
  - ION/02_architecture/BRANCH_DELEGATION_ROUTER_PROTOCOL.md
  - ION/02_architecture/LAWFUL_ORCHESTRATION_SCHEDULER_PROTOCOL.md
  - ION/02_architecture/BOUNDED_PARALLELISM_AND_SETTLEMENT_PROTOCOL.md
  - ION/05_context/signals/20260515_carrier_portable_working_intelligence_journal.md
  - ION/07_templates/context/ION_BRANCH_CONTEXT_CAPSULE_CANDIDATE.template.yaml
  - ION/07_templates/context/ION_BRANCH_CONTEXT_MATERIALIZATION_RECEIPT.template.yaml
  - ION/04_packages/kernel/ion_branch_context_materialization.py
---

# Lazy Branch Context Materialization Protocol

## Core Law

```text
CONTEXT_GROWS_WHERE_WORK_HAPPENS
```

ION does not pre-materialize `README.md`, `AGENTS.md`, or
`ION_CONTEXT_CAPSULE.yaml` for every folder. A folder inherits parent/root
context until real work enters it and proves that a local context boundary would
help the next carrier.

An empty folder is not a failed branch. It is an unmaterialized branch.

## Relationship To README Branch Context

`README_BRANCH_CONTEXT_PROTOCOL.md` defines mature branch context nodes and the
existing `B0_inert_folder` through `B6_automation_ready_branch` ladder. This
protocol governs the earlier entry moment before a folder has become a complete
branch node.

```text
worker enters folder
-> inspect local and parent context
-> classify lazy maturity
-> inherit, propose, create candidate, skip, or block
-> continue the original task
-> emit a materialization receipt when context changed or a decision matters
```

Lazy materialization does not grant accepted state. Candidate context remains
candidate until review, settlement, or an explicit acceptance path promotes it.

## Lazy Maturity Levels

```yaml
lazy_branch_context_maturity:
  level_0_absent:
    meaning: No local context exists. Parent/root context applies.
    branch_protocol_relation: B0_inert_folder
  level_1_inherited:
    meaning: A worker inspected the folder and recorded that parent context is enough for now.
    branch_protocol_relation: B0_inert_folder with explicit inheritance receipt
  level_2_stub:
    meaning: Minimal local README, marker, or entry hint exists, but no full branch contract exists.
    branch_protocol_relation: B1_readme_entry or marker-only candidate
  level_3_candidate:
    meaning: First lawful worker inspected the folder and created or proposed candidate context.
    branch_protocol_relation: candidate precursor to B2_capsule_node
  level_4_active:
    meaning: Branch has receipts, active memory, known templates, routes, or agents.
    branch_protocol_relation: B3_routed_branch or B4_agentic_branch evidence expected
  level_5_reviewed:
    meaning: Reviewer, Nemesis, Steward, or equivalent review has inspected the context.
    branch_protocol_relation: reviewed candidate branch node
  level_6_accepted:
    meaning: Local branch context can act as local branch authority for future workers.
    branch_protocol_relation: accepted branch node with receipts and authority boundary
```

The lazy level is an entry/materialization posture. It does not replace the
README branch context maturity enum used by complete branch nodes.

## First Lawful Branch Entry

A first lawful branch entry happens when a carrier is already doing real work
that touches a folder, file, domain, or route. It is not permission to fan out
across the repository looking for missing capsules.

Before materializing, the carrier must:

1. Resolve the active objective and work packet.
2. Determine the folder being entered.
3. Search upward for parent `README.md`, `ION_CONTEXT_CAPSULE.yaml`, or branch
   capsule context.
4. Inspect local `README.md`, `ION_CONTEXT_CAPSULE.yaml`, `AGENTS.md`,
   `SKILL.md`, templates, tests, routes, schemas, and obvious source markers.
5. Classify the folder as inherited, materializable branch, local stub,
   existing branch context, non-branch utility folder, generated artifact,
   vendor/cache, unsafe/ignored, or blocked.
6. If parent context is enough, record the inheritance decision when the
   decision is material.
7. If missing local context blocks or slows future carriers, create or propose a
   compact candidate context.
8. Continue the original task. Do not turn context creation into unrelated
   busywork.

## Local Context Files

```yaml
local_context_files:
  README.md:
    role: human and generic-AI branch entry surface
    authority: projection_not_state
  ION_CONTEXT_CAPSULE.yaml:
    role: machine-readable branch contract
    authority: local_context_contract_when_reviewed_or_accepted
  AGENTS.md:
    role: carrier-native standing instructions for the subtree
    authority: scoped carrier contract only when needed
  .agents/skills/<branch-skill>/SKILL.md:
    role: repeatable operating procedure
    authority: procedure, not project memory
  templates:
    role: inherited by default; branch-local only when divergence is proven
  receipts:
    role: evidence for materialization, inheritance, review, and acceptance
```

Templates should stay central or parent-owned unless branch-specific divergence
is proven by real work.

## Materialization Decisions

```yaml
decisions:
  created:
    meaning: Candidate context file or receipt was written under explicit local write authority.
  proposed:
    meaning: Candidate capsule data was built but not written as local branch authority.
  inherited:
    meaning: Parent context is enough for the current task.
  not_branch:
    meaning: Folder is ignored, generated, vendor/cache, or not a meaningful branch boundary.
  blocked:
    meaning: Path is missing, unsafe, unreadable, or required parent context cannot be resolved.
```

Default carrier behavior is dry-run/candidate. Writing a receipt or candidate
context must be an explicit operation. Existing local capsules must not be
overwritten by default.

## Ignore And Exclusion Rules

Do not materialize branch context for:

- `.git`
- `node_modules`
- `venv` or `.venv`
- `dist`
- `build`
- `cache` or cache directories
- `__pycache__`
- generated binary/archive artifacts
- vaults, secrets, credentials, or token lanes
- external vendor trees unless explicitly routed
- quarantine/archive witness material unless a bounded packet promotes a file

Ignoring a path is not a failure. It is a lawful `not_branch` decision.

## Candidate Capsule Contract

Candidate capsules use:

```text
ION/07_templates/context/ION_BRANCH_CONTEXT_CAPSULE_CANDIDATE.template.yaml
```

Required fields:

```yaml
schema_id: ion.branch_context_capsule_candidate.v0_1
branch_id: <slug>
path: <relative/path>
parent_branch_ref: <nearest parent context>
maturity_level: level_3_candidate
purpose: <compact reason this folder may need local context>
when_to_enter: []
read_first: []
local_templates: []
local_agents_or_roles: []
allowed_operations: []
receipts_path: ION/05_context/current/branch_context_materialization/receipts
known_blockers: []
escalation_routes: []
last_updated: <iso8601>
accepted_state_claim: false
```

The candidate capsule is a proposal. It is not accepted local branch authority.

## Materialization Receipt Contract

Receipts use:

```text
ION/07_templates/context/ION_BRANCH_CONTEXT_MATERIALIZATION_RECEIPT.template.yaml
```

Required fields:

```yaml
schema_id: ion.branch_context_materialization_receipt.v0_1
branch_path: <relative/path>
parent_context_used: {}
local_files_inspected: []
classification: <classification>
decision: created|proposed|inherited|not_branch|blocked
touched_paths: []
created_file_sha256: {}
next_carrier_instructions: []
accepted_state_claim: false
```

Receipts preserve the entry decision and file hashes for any created context
files. A receipt does not promote the candidate context to accepted state.

## Integration Points

### Codex Carrier Sync Layer

- `UserPromptSubmit` can suggest lazy branch materialization when a prompt
  names a folder/domain that lacks local context.
- `PreCompact` can preserve branch baton refs when materialization happened
  during the turn.
- `Stop` can include materialization receipt refs in its turn handoff.
- Hooks must not automatically mutate `HOT_CONTEXT.md`, `CAPSULE.md`, or local
  branch capsules under this protocol.

### Skills

- `ion-orchestration` should treat branch entry as a context-routing step before
  substantive work.
- `ion-context-scout` should search parent and local capsules first, then
  propose materialization only when the folder becomes real work.
- `ion-workbench` may include the lazy maturity level in context packages.

### MCP / Actions Branch Leaders

Future `ion_branch_describe` and `ion_branch_invoke` tools should use the same
lazy maturity model:

```text
path reference
-> nearest parent context
-> local context classification
-> candidate materialization route when useful
-> bounded branch operation or receipt
```

### Subagents

Subagents should receive the branch classification, parent context ref, and any
candidate capsule data in their bounded context package. They must not claim a
local branch context exists unless they inspected or received proof of it.

## Success Condition

Lazy materialization succeeds when the next carrier can tell whether a folder is:

- inherited from a parent context;
- a materializable branch with a candidate capsule;
- already a local branch context;
- intentionally ignored or not a branch; or
- blocked with explicit missing proof.

The repository remains free of mass scaffold noise, and branch-local context
appears only where real work made it useful.
