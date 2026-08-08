# GitHub Repository Platform Governance — Operating Card

```yaml
schema_id: ion.domain.github_repository_platform_governance.operating_card.v0_1_candidate
domain_id: domain.github_repository_platform_governance
wave: MITOSIS_CHILD
priority: P1
class: MITOSIS_CHILD
status: candidate_only
registry_promotion: false
projection_mutation: false
activation_packet: PCKT-ION-LEAD-ORCHESTRATION-GITHUB-PLATFORM-DOMAIN-CANDIDATE-ACTIVATION-20260725
materialized_at: 2026-07-26T00:03:00Z
```

## Purpose

Narrow mitosis child domain for GitHub **platform surface** governance on `ION-operations/ION-Production`. Owns read models and policy proposals for repository settings, branch protection, Actions, CODEOWNERS, and PR governance. Does **not** own local git operations, commit manifests, or accepted merge truth.

## Owned vs not owned

| Owns | Does not own |
| --- | --- |
| GitHub settings read model | `git add` / commit / push |
| Branch protection / rulesets **proposals** | Working-tree tier inventory |
| Actions/CI relationship mapping | Pre-commit gate execution |
| CODEOWNERS / PR template policy | Accepted merge rank |
| Platform change receipts | Production release cutover |

## Continuity templates

Folder-local templates under `continuity_templates/`:

1. `REPOSITORY_ORIENTATION.candidate.md` — bind to remote + branch
2. `PLATFORM_READ_MODEL.candidate.yaml` — settings snapshot schema
3. `BRANCH_PROTECTION_PROPOSAL.candidate.yaml` — ruleset proposal shell
4. `ACTIONS_POLICY.candidate.yaml` — workflow/check relationship
5. `CODEOWNERS_POLICY.candidate.md` — ownership proposal shell
6. `PR_GOVERNANCE.candidate.yaml` — draft PR workflow policy
7. `PLATFORM_CHANGE_RECEIPT.candidate.md` — record platform-side proposals

## Required worker reads

1. `domain.github_repository_platform_governance.domain.candidate.yaml`
2. `DOMAIN_RELATIONSHIPS.candidate.yaml`
3. `CONTEXT_REQUIREMENTS.candidate.yaml`
4. Parent decision: `../domain.domain_mitosis_and_agent_society_formation/evolution_packets/PCKT-GITHUB-REPOSITORY-GOVERNANCE-DOMAIN-ASSEMBLY-20260725_DECISION.candidate.yaml`

## Specialist mount

- `role.github_repository_platform_governance_steward` → `codex_agent_mounts/role_github_repository_platform_governance_steward__domain_github_repository_platform_governance/`

## Refusal rules

- No GitHub API mutation without operator gate and separate activation packet
- No branch protection apply in candidate activation
- No secrets or credential access
- No registry promotion to `ION/03_registry/`
