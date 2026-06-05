# ION Agent Branch Capsule Material Work Guard Protocol v0.1

Status: candidate consolidated protocol
Packet: PCKT-ION-BRANCH-CAPSULE-CONSOLIDATION-006

## Purpose

Guard material edits so each agent writes only inside an explicit branch scope
and cannot mutate shared context, accepted-state surfaces, or checkpoint
authority by accident.

## Required preflight

Before material edits, a worker must prove:

- Branch identity is present.
- `settlement_required` is true.
- `accepted_state_authority` is false.
- `write_scope` is declared.
- Requested paths are inside declared `write_scope`.
- Requested paths do not target shared Capsule/Mini/HOT_CONTEXT/STATUS/ROUTE.
- Requested paths do not assign C-numbers, checkpoints, or accepted-state.
- Practical write-scope collisions are surfaced.

## Shared context block

These surfaces are read-only for branch workers unless a separate bounded packet
explicitly grants authority:

- `ION/05_context/current/codex_solo/CAPSULE.md`
- `ION/05_context/current/codex_solo/MINI.md`
- `ION/05_context/current/codex_solo/HOT_CONTEXT.md`
- `ION/05_context/current/codex_solo/STATUS.json`
- `ION/05_context/current/codex_solo/ROUTE.json`
- `ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json`

## Guard verdicts

- `BRANCH_GUARD_READY`
- `BRANCH_GUARD_BLOCKED`

Blocked findings are evidence, not failure theater. The correct next step is a
bounded repair or a settlement note, not a silent override.
