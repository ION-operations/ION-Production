---
type: architecture_protocol
authority: A3_CANDIDATE
created: 2026-05-15T00:00:00-04:00
status: CANDIDATE
protocol_id: ion_action_mcp_branch_leader_gateway_protocol
purpose: Define the Action/MCP branch leader gateway as a bounded routing surface over ION branch context and owner tools.
connections:
  - ION/02_architecture/LAZY_BRANCH_CONTEXT_MATERIALIZATION_PROTOCOL.md
  - ION/02_architecture/README_BRANCH_CONTEXT_PROTOCOL.md
  - ION/02_architecture/BRANCH_DELEGATION_ROUTER_PROTOCOL.md
  - ION/03_registry/ion_action_mcp_branch_leader_registry.yaml
  - ION/04_packages/kernel/ion_action_mcp_branch_leaders.py
---

# ION Action/MCP Branch Leader Gateway Protocol

## Purpose

The branch leader gateway prevents Action and MCP carriers from treating ION as
one flat list of tools. A carrier asks a branch leader what a branch can do, then
invokes one declared route when authority and proof requirements are satisfied.

```text
carrier asks for branch/path
-> branch leader describes context, maturity, routes, receipts, and blockers
-> carrier invokes one bounded route
-> owner tool or local branch-context adapter handles the route
-> return includes proof and authority boundary
```

## Lazy Context Integration

Branch leaders must support folders that do not yet have local capsules.

`ion_action_branch_describe` may receive either a registry `branch_id` or a repo
path. If a local context node exists, it reports that context. If no local
context exists, it calls the lazy branch context helper and returns:

- branch path and synthetic branch id;
- lazy maturity level;
- parent context;
- local context files inspected;
- `candidate_available`;
- suggested next calls;
- allowed operations;
- receipt path;
- blocker for ignored, generated, missing, vendor, vault, or quarantine paths.

Describe is read-only. It must never create context files.

## Branch Context Routes

The `branch_context` branch leader owns local routes:

```yaml
describe_path:
  meaning: describe one repo path using lazy context classification
  write: never
inherit_parent_context:
  meaning: build or optionally write a materialization receipt saying parent context applies
  write: only when write=true, idempotency_key exists, and confirmation matches
materialize_candidate_context:
  meaning: build or optionally write candidate branch context
  write: only when write=true, idempotency_key exists, and confirmation matches
```

Candidate materialization writes `ION_CONTEXT_CAPSULE.candidate.yaml`, not
`ION_CONTEXT_CAPSULE.yaml`. The candidate file is not accepted state or local
branch authority until reviewed and promoted through normal ION law.

## Boundaries

- No broad universal execute-anything endpoint.
- No production authority.
- No live execution authority.
- No credentials authority.
- No automatic branch context writes from describe.
- No overwriting existing `ION_CONTEXT_CAPSULE.yaml`.
- No mass folder materialization.

## Success Condition

The carrier can navigate branch context through a small branch-leader surface:

```text
ion_action_branch_list
ion_action_branch_describe
ion_action_branch_invoke
ion_action_branch_receipts
```

That surface is sufficient to discover branch maturity, route next calls, and
materialize candidate context only through explicit confirmation-gated invoke.
