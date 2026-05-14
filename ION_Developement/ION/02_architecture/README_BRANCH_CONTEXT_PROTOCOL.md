---
type: architecture_protocol
authority: A3_CANDIDATE
created: 2026-05-14T00:00:00-04:00
status: CANDIDATE
protocol_id: readme_branch_context_protocol
purpose: Make the repository itself a navigational context substrate by turning README files and local context capsules into branch-native AI entrypoints.
connections:
  - ION/02_architecture/CONTEXT_GRAPH_SUBSTRATE_PROTOCOL.md
  - ION/02_architecture/CONTEXT_NODE_AND_PACKAGE_PROTOCOL.md
  - ION/02_architecture/EVENTED_TEMPLATE_FILE_GRAPH_PROTOCOL.md
  - ION/02_architecture/CONTEXT_PERFECT_CONTINUATION_PROTOCOL.md
  - ION/02_architecture/FRONT_DOOR_SELF_MOUNT_BINDING_PROTOCOL.md
  - ION/02_architecture/CONVERSATIONAL_RECEIPT_AND_LIVE_REPAIR_PROTOCOL.md
  - ION/03_registry/ion_branch_context_node.schema.json
  - ION/03_registry/ion_branch_context_policy.yaml
  - ION/07_templates/context/README_BRANCH_NODE.template.md
  - ION/07_templates/context/ION_CONTEXT_CAPSULE.branch.template.yaml
---

# README Branch Context Protocol

## Posture

This is ION-wide candidate architecture law. It is not limited to the Custom GPT
carrier, the browser extension, Codex, Cursor, MCP, or any one execution surface.
It does not grant production authority, live execution authority, accepted-state
authority, or secrets access.

The protocol turns ordinary repository navigation into lawful ION context
orientation: a generic AI, human, worker, or tool that enters a folder should be
able to open `README.md`, discover the local `ION_CONTEXT_CAPSULE.yaml`, follow
parent and child branch edges, inspect receipts, and know what it may do next
without reconstructing ION from ambient memory.

## Core Thesis

ION should not require an agent to read a disconnected document and then infer
which context package, template, protocol, or agent role applies. The folder is
the natural context boundary. The README is the natural entry surface. The local
capsule is the machine-readable operating contract. Parent and child branches
form the navigational context web.

```text
old pattern:
  agent enters folder
  agent searches docs
  agent guesses context
  agent guesses authority
  agent chooses workflow

new pattern:
  agent enters folder
  agent opens README.md
  README points to ION_CONTEXT_CAPSULE.yaml
  capsule declares parent chain, local surfaces, receipts, routes, templates, agents
  agent follows bounded read order
  agent emits candidate work or blocker with proof posture
```

## README_BRANCH_CONTEXT_LAW

Every significant ION folder should become a branch context node when it carries
local meaning, authority, workflow, templates, agents, receipts, or operational
risk.

A branch context node has two public faces:

1. `README.md` — human and generic-AI entry projection.
2. `ION_CONTEXT_CAPSULE.yaml` — machine-readable operating contract.

The README may teach and summarize. The capsule governs local read order,
branch edges, local routes, templates, agents, receipts, authority boundaries,
and continuity export rules.

## README_PROJECTION_NOT_STATE_LAW

A README is not accepted state by itself.

A README may:
- orient a human or generic AI;
- summarize lower branches;
- point to receipts;
- name local workflows;
- name local authority limits;
- provide safe-entry steps.

A README may not:
- grant production authority;
- grant live execution authority;
- erase missing proof;
- override a parent capsule;
- override current operator instruction;
- convert chat output into accepted state without receipt;
- silently mutate the context graph.

## CAPSULE_FIRST_LAW

For serious ION work inside a branch node, the safe entry sequence is:

1. Read `README.md`.
2. Read `ION_CONTEXT_CAPSULE.yaml`.
3. Read parent capsules listed by `parent_domain` or `parent_chain`.
4. Read local `read_first` files.
5. Inspect local receipts/status before state-bearing claims.
6. Select a local route/template/agent only if declared.
7. Emit a candidate result, blocker, receipt fragment, or continuation envelope.

If the capsule is missing, stale, contradictory, or unreadable, the worker must
degrade or block rather than invent local law.

## NATURAL_AI_ENTRY_LAW

The protocol is designed for untrained or weakly-instructed AI behavior. A model
that simply opens `README.md` should find enough local entry instructions to
avoid blind operation.

Each branch README should therefore include a compact entry section with:
- “Read this first”;
- pointer to `ION_CONTEXT_CAPSULE.yaml`;
- local purpose;
- branch position;
- authority boundary;
- safe work;
- approval-required work;
- receipts/history;
- continuity export instructions.

## BRANCH_AS_CONTEXT_PACKAGE_LAW

A branch node is a folder-native context package.

The branch package consists of:
- the README projection;
- the machine capsule;
- local protocols and route files;
- local templates and schemas;
- local agent/role files;
- local tests;
- local receipts and status files;
- parent capsule summaries;
- child branch index summaries.

External context packages may be exported from a branch node, but the branch
itself is the canonical navigational substrate.

## PARENT_CHILD_CONTEXT_GRAVITY_LAW

Branches form a context-gravity web.

- A child branch points upward to the parent chain for inherited authority and
  summary.
- A parent branch summarizes children enough for navigation, not enough to
  pretend it fully contains every child.
- Sibling branch use requires explicit edge, index, or route.
- Lower branches may be specialized and dense.
- Higher branches should compress, index, and route.

This prevents the root from becoming an unreadable dump while preventing leaves
from becoming orphaned context islands.

## BRANCH_MATURITY_LEVELS

```yaml
maturity_levels:
  B0_inert_folder:
    meaning: no ION branch contract
    allowed: ordinary file evidence only
  B1_readme_entry:
    meaning: README has branch entry section
    allowed: human/generic_AI orientation
  B2_capsule_node:
    meaning: README plus ION_CONTEXT_CAPSULE.yaml exist and parse
    allowed: local context package mount candidate
  B3_routed_branch:
    meaning: declared routes/templates/schemas/tests/receipts
    allowed: bounded local workflow selection
  B4_agentic_branch:
    meaning: declared local agents or role mounts
    allowed: domain-specific agent delegation when authority permits
  B5_evented_graph_branch:
    meaning: template-instantiated files and receipts can trigger lawful reactions
    allowed: evented graph operations after validation
  B6_automation_ready_branch:
    meaning: tests, receipts, authority, and runtime hooks are proven
    allowed: governed automation within explicit authority
```

A branch may claim only the maturity level supported by files and receipts.

## REQUIRED CAPSULE FIELDS

The local capsule should validate against
`ION/03_registry/ion_branch_context_node.schema.json`.

Minimum operational fields:
- `schema_id`
- `branch_id`
- `branch_label`
- `path`
- `maturity_level`
- `purpose`
- `authority`
- `parent_domain` or `parent_chain`
- `read_order`
- `local_surfaces`
- `receipts`
- `continuity_export`
- `tags`

## LOCAL SURFACES

A branch may declare:

```yaml
local_surfaces:
  protocols: []
  routes: []
  templates: []
  schemas: []
  agents: []
  registries: []
  tests: []
  receipts: []
  status: []
  child_index: []
```

A surface is a pointer, not proof. The worker must still inspect the file before
using it as evidence.

## EDGE TYPES

```yaml
branch_edge_types:
  parent_of: higher branch summarizes and routes to child
  child_of: child inherits parent authority context
  sibling_of: explicit peer navigation relation
  depends_on: branch requires another branch to operate
  implements: branch implements a protocol/template/route
  evidenced_by: branch claim is backed by receipt/status/test
  supersedes: branch replaces an older branch surface
  contradicts: branch conflicts with another claim and needs review
  exports_to: branch can materialize external context package
  owned_by: branch has declared custodian or role owner
```

## RECEIPT AND STATUS LAW

Every serious branch node should expose a local receipt/status surface.

The receipt surface may include:
- durable receipts;
- candidate chat receipt fragments;
- latest status summaries;
- test reports;
- settlement notes;
- blockers;
- continuity exports.

Chat YAML blocks may become candidate receipt fragments, but they are not
accepted state until landed into an approved receipt path or accepted by the
operator/system with proof.

## TAG LAW

Tags may help browsers, prompt libraries, queue packs, context packages, and
worker UIs navigate the branch graph.

Recommended tag shape:

```yaml
reserved_tag_namespaces:
  branch:
    examples: [root, architecture, carrier, extension, context]
  node:
    examples: [readme, capsule, template, protocol, receipt]
  route:
    examples: [boot-sequence, persona-return, context-sync]
  phase:
    examples: [ingress, relay, steward, mason, nemesis, scribe, persona]
  state:
    examples: [candidate, validated, blocked, missing-proof]
  authority:
    examples: [read-only, approval-required, no-production, no-live]
  proof:
    examples: [source-inspected, tool-call, artifact-created, test-pass, missing]
```

Tags never grant authority, accepted state, proof, or receipt status.

## BRANCH ENTRY ALGORITHM

```yaml
branch_entry_algorithm:
  - locate_current_folder
  - open_README_md
  - if README declares ION branch node, read ION_CONTEXT_CAPSULE_yaml
  - parse capsule and normalize tags
  - mount parent_chain in declared order
  - inspect read_first files
  - inspect receipts/status before claims
  - select declared route/template/agent if applicable
  - run safe checks if needed
  - emit candidate work, blocker, receipt, or continuation envelope
```

## MIGRATION PLAYBOOK

```yaml
migration_stages:
  stage_0_inventory:
    objective: find significant folders and existing README/capsule/status surfaces
  stage_1_root_and_major_domains:
    objective: add branch entry sections and capsules to root, ION/, architecture, registry, templates, packages, context, tests
  stage_2_domain_nodes:
    objective: add local branch nodes where work naturally enters
  stage_3_route_template_agent_binding:
    objective: connect local routes, templates, schemas, agents, and tests
  stage_4_receipt_surfaces:
    objective: expose local receipts/status and continuity export rules
  stage_5_validation:
    objective: run branch validator and prevent maturity overclaim
  stage_6_ui_and_extension:
    objective: let browser extension/cockpit show branch tags, receipt blocks, and missing proof
```

## FAILURE MODES

```yaml
failure_modes:
  orphan_readme:
    meaning: README gives instructions but no capsule exists
    response: degrade to B1 and create capsule TODO/blocker
  orphan_capsule:
    meaning: capsule exists but README does not point to it
    response: degrade and patch README projection
  maturity_overclaim:
    meaning: capsule claims B4/B5/B6 without surfaces/tests/receipts
    response: block maturity claim
  parent_chain_break:
    meaning: parent capsule missing or contradictory
    response: block inherited authority claims
  tag_authority_confusion:
    meaning: tag implies proof or approval
    response: ignore tag as authority and create finding
  context_dump_root:
    meaning: root README attempts to contain all lower detail
    response: split into parent summaries plus child index
```

## Relationship To Existing ION Law

This protocol does not replace the context graph. It materializes the graph in
the repository structure that humans and models naturally traverse.

- Context graph substrate says ION is a governed graph.
- Context node/package protocol gives node and package shapes.
- Evented template file graph says lawful files can become graph objects.
- Context-perfect continuation requires bounded continuation bundles.
- README branch context protocol makes the folder/README/capsule trio the
  default navigational projection of those laws.

## Acceptance Conditions

This candidate protocol should not be treated as accepted ION-wide law until:
- the schema and templates land in the repo;
- validator tests pass;
- root and major-domain pilot capsules are created;
- browser extension/cockpit tag behavior is aligned;
- an operator or governance receipt accepts the migration path.
