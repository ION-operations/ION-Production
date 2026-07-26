# ION Agent Mount HOT_CONTEXT

generated_at: 2026-07-26T00:03:00+00:00
context_id: wcaps_github_platform_gov_20260726
mount_id: role_github_repository_platform_governance_steward__domain_github_repository_platform_governance
role_id: role.github_repository_platform_governance_steward
domain_id: domain.github_repository_platform_governance
candidate_mount_only: true
production_authority: false
live_execution_authority: false
accepted_state_authority: false
secrets_authority: false

## Repository binding

- repository_slug: ION-operations/ION-Production
- primary_remote: https://github.com/ION-operations/ION-Production.git
- active_branch: codex/ion-custom-gpt-front-door-carrier-v4
- shell_root: /home/sev/ION - Production/ION_Developement

## Working Context

- active_context_package: .ion/ACTIVE_CONTEXT_PACKAGE.md
- domain_charter: ION/05_context/current/domain_weaver/candidate_founding_domains/domain.github_repository_platform_governance/
- initial_packet: packets/PCKT-GITHUB-PLATFORM-READONLY-ORIENTATION-20260725.candidate.yaml

## Rules

- Platform surface only — no local git or GitHub mutation in candidate posture.
- Local commit and push require branch_fabric + artifact_provenance gates outside this domain.
- Emit candidate receipts under `.ion/receipts` for material work.
