# ION Agent Branch Capsule Settlement Intake Protocol v0.1

Status: candidate consolidated protocol
Packet: PCKT-ION-BRANCH-CAPSULE-CONSOLIDATION-006

## Purpose

Normalize how candidate branch work asks to be reviewed without claiming that a
Codex return, patch, or diff has already become accepted ION state.

## Required intake fields

A branch settlement request must carry:

- `packet_id`
- `branch_identity`
- `requested_write_scope`
- `loaded_refs`
- `guard_evidence`
- `workload_diff`
- `result_summary`
- `settlement_request`
- `authority`
- `non_claims`

## Branch identity

`branch_identity` must include:

- `context_instance_id`
- `branch_id`
- `agent_tag`
- `conversation_tag`
- `parent_context_id`

## Intake blocks

Settlement intake must block or flag:

- Missing branch identity.
- Missing guard evidence.
- Guard evidence that is not ready.
- Missing workload diff.
- Shared context surfaces used as merge source.
- Direct accepted-state merge requests.
- Checkpoint or C-number assignment by the branch.
- Any accepted-state authority claim.

## Result

Intake may mark a branch request ready for review. It does not merge accepted
state by itself.
