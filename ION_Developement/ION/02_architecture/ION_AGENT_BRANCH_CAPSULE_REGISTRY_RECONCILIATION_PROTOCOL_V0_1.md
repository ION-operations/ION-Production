# ION Agent Branch Capsule Registry Reconciliation Protocol v0.1

Status: candidate consolidated protocol
Packet: PCKT-ION-BRANCH-CAPSULE-CONSOLIDATION-006

## Purpose

Keep the local branch registry useful as an operator/Steward surface without
turning it into accepted state.

## Reconciliation checks

Reconciliation should report:

- Registry rows with no branch record.
- Branch records with no registry row.
- Stale or malformed branch rows.
- Active write-scope collisions.
- Shared context paths inside write scopes.
- Missing settlement requests for branches that require settlement.

## Health snapshot

The cockpit or local tooling may render:

- registered branch count
- branch record count
- active branch count
- reconciliation verdict
- findings list

## Authority boundary

Reconciliation reports are candidate operational evidence. They do not assign
C-numbers, approve merges, or mutate shared context as accepted state.
