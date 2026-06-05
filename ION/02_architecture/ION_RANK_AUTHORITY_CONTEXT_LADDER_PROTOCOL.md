# ION Rank Authority Context Ladder Protocol v0.1

Status: candidate local protocol
Packet: CODEX_B3_RANK_AUTHORITY_LADDER
Production authority: false
Live execution authority: false
Accepted state claim: false
Secrets authority: false

## Core Law

Rank is not superiority.

Rank is settlement height in the context graph:

```text
rank = context elevation + authority scope + mutation class + proof burden
```

Rank is not persona, human worth, model quality, or permanent identity. Rank is
a bounded settlement rule for a specific candidate output.

## Rank Ladder

```text
R0_WITNESS
R1_LOCAL_WORKER
R2_DOMAIN_WORKER
R3_BRANCH_INTEGRATOR
R4_SETTLEMENT_STEWARD
R5_ROOT_GOVERNOR
R6_HUMAN_AUTHORITY
```

Each rank is represented as a vector:

```yaml
rank_id:
context_level:
domain_scope:
mutation_class:
settlement_power:
proof_burden:
expiry:
```

## Settlement Law

Lower-rank workers cannot self-promote candidate work into accepted settlement.
They may return evidence, recommendations, validation, and handoff notes.

`R3_BRANCH_INTEGRATOR` may reconcile branch or wave context, but promotion of
that reconciliation requires `R4_SETTLEMENT_STEWARD` sign-off.

`R4_SETTLEMENT_STEWARD` may settle candidate returns when evidence is present.
It cannot grant production authority, live execution authority, secret access,
deployment authority, GitHub push authority, or root/profile mutation authority.

`R5_ROOT_GOVERNOR` may prepare root-law or profile mutation decisions only when
an explicit human approval gate is present.

`R6_HUMAN_AUTHORITY` is an explicit operator approval or rejection, not an AI
rank escalation.

## C1 Branch-Integrator Case

`codex_c1_wave_reconcile` is the first real branch-integrator case for this
candidate ladder.

It is classified as:

```yaml
true_name: codex_c1_wave_reconcile
rank_id: R3_BRANCH_INTEGRATOR
primary_domain: context.wave
mutation_class: branch_reconciliation
settlement_power: recommend_branch_promotion_only
```

The Wave 001/002 reconciliation report, ledger, and Wave 003 plan-only report
remain candidate evidence. C1 may recommend promotion. C1 may not self-accept
or promote its own reconciliation. Promotion requires R4 settlement.

## Non-Authority

This protocol grants no production authority, live execution authority,
accepted-state authority, secret authority, deployment authority, or GitHub push
authority.

## Implementation

```text
ION/04_packages/kernel/ion_rank_authority.py
ION/07_templates/settlement/RANKED_SIGNOFF_TEMPLATE.md
ION/05_context/current/worker_shift/rank_bindings/
```
