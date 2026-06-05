---
schema_id: ion.readme_branch_node_template.v0_2
status: CANDIDATE_TEMPLATE
purpose: Human and generic-AI README projection for an ION branch context node.
---

# <Branch Label> — ION Branch Context Node

## Enter Here

This folder is an ION branch context node.

Before substantive work:

1. Read this README.
2. Read `ION_CONTEXT_CAPSULE.yaml`.
3. Follow the capsule `parent_chain` upward before claiming inherited context.
4. Read the local `read_order` files.
5. Check local receipts/status before claiming state.
6. Use only declared local routes/templates/agents.
7. If proof is missing, emit a blocker or candidate receipt fragment.

## Purpose

<What this branch owns and why it exists.>

## Branch Position

```yaml
branch:
  branch_id: <branch_id>
  maturity_level: B2_capsule_node
  parent_domain: <parent_branch_or_root>
  child_domains:
    - <child_branch_id>
```

## Authority

```yaml
authority:
  accepted_state_claim: false
  production_authority: false
  live_execution_authority: false
  default_work_authority: read_only_or_sandbox_candidate
  approval_required_for:
    - production_write
    - live_execution
    - connector_mutation
    - accepted_state_landing
```

## Read First

- `ION_CONTEXT_CAPSULE.yaml`
- `<local_protocol_or_index>`
- `<latest_status_or_receipt>`

## Local Surfaces

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

## Safe Work

<Reads, lints, parse checks, documentation patches, test-only checks, sandbox candidate artifacts.>

## Approval Required

<Writes, connector actions, production/live work, secrets access, acceptance/landing.>

## Receipts / History

<List latest receipts, test reports, status files, and settlement notes.>

## Child Branches

| Child | Purpose | Entry |
| --- | --- | --- |
| `<child>` | `<summary>` | `<path>/README.md` |

## Continuity Export

A context export for this branch should include this README, `ION_CONTEXT_CAPSULE.yaml`,
local read-first files, declared route/template/schema/agent surfaces, relevant tests,
and latest receipts. It should not include secrets or unrelated child detail.

## Do Not

- Do not treat this README as accepted state.
- Do not claim production or live authority from this folder.
- Do not skip receipts when making state-bearing claims.
- Do not silently widen into sibling or child branches.
