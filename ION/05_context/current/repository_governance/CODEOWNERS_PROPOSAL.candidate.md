# CODEOWNERS Proposal (candidate)

schema_id: ion.repository_governance.codeowners_proposal.v0_1_candidate
owner_domain_id: domain.github_repository_platform_governance
repository_slug: ION-operations/ION-Production
status: candidate_populated_from_remote_read_model
materialized_at: 2026-07-26T00:16:00Z
materialized_by_packet: PCKT-GITHUB-PLATFORM-BRANCH-PROTECTION-READMODEL-20260725
canonical_promotion_target: ION/05_context/current/repository_governance/CODEOWNERS_PROPOSAL.candidate.md

## Purpose

Maps repository paths to **ION domain ownership** for review routing and accountability. CODEOWNERS-style review requests do **not** grant merge authority, accepted-state rank, or production release authority. Merge rank remains with `domain.state_rank_and_receipt_truth`.

## Observed platform state (read-only)

| Check | Result |
| --- | --- |
| `ION_Developement/.github/CODEOWNERS` | **absent** |
| `/home/sev/ION - Production/.github/CODEOWNERS` | **absent** |
| GitHub CODEOWNERS on remote | **not observed** (`codeowners_observed: false`) |
| CODEOWNERS enforcement on remote | **unknown** (branch protection plan-limited) |

## ION domain path mapping (proposal — not applied)

| Path pattern | ION domain owner | GitHub team handle (proposal) | Authority note |
| --- | --- | --- | --- |
| `/ION/04_packages/` | `domain.context_systems` (kernel runtime) | `@ION-operations/kernel-maintainers` | review routing only |
| `/ION/07_templates/` | `domain.context_systems` | `@ION-operations/template-curators` | review routing only |
| `/ION/03_registry/` | `domain.context_systems` | `@ION-operations/template-curators` | review routing only |
| `/ION/05_context/` | `domain.context_systems` + `domain.domain_weaver_living_self_model` | `@ION-operations/context-stewards` | review routing only |
| `/ION/05_context/current/repository_governance/` | `domain.github_repository_platform_governance` | `@ION-operations/context-stewards` | review routing only |
| `/ION/05_context/current/domain_weaver/` | `domain.domain_weaver_living_self_model` | `@ION-operations/context-stewards` | review routing only |
| `/.github/` (workspace root) | `domain.github_repository_platform_governance` | `@ION-operations/context-stewards` | Actions/CI platform surface |
| `/.github/` (git toplevel) | `domain.github_repository_platform_governance` | `@ION-operations/context-stewards` | issue/PR templates |
| `*` (default) | `domain.domain_mitosis_and_agent_society_formation` (parent) | `@ION-operations/ion-core` | review routing only |

Path cartography authority: `domain.context_graph_branch_fabric`. Provenance gates: `domain.artifact_provenance_and_gate_legitimacy`.

## Draft CODEOWNERS file (illustrative — not committed)

```text
# ION domain ownership mapping — review routing only; no merge authority
# Platform domain: domain.github_repository_platform_governance

/ION/04_packages/                                      @ION-operations/kernel-maintainers
/ION/07_templates/                                     @ION-operations/template-curators
/ION/03_registry/                                      @ION-operations/template-curators
/ION/05_context/current/repository_governance/         @ION-operations/context-stewards
/ION/05_context/current/domain_weaver/                 @ION-operations/context-stewards
/ION/05_context/                                       @ION-operations/context-stewards
/.github/                                              @ION-operations/context-stewards
*                                                      @ION-operations/ion-core
```

## Relationship to branch protection proposal

When GitHub plan allows branch protection apply:

- `require_code_owner_reviews: true` in `BRANCH_PROTECTION_PROPOSAL.candidate.yaml`
- CODEOWNERS file must exist at `.github/CODEOWNERS` (git toplevel) or workspace root per GitHub resolution rules
- Until then, ION fallback policy enforces review via draft-PR and push-receipt gates

## Gates before file write or GitHub apply

- `BLK-WORKING-TREE-UNCLASSIFIED` closed
- `BLK-REBASE12-FORENSIC` closed
- Operator confirmation of GitHub team handles
- Separate activation packet for CODEOWNERS commit

## Non-claims

Proposal only. No CODEOWNERS file committed. No GitHub mutation. Domain mapping is ION accountability — not merge authority.
