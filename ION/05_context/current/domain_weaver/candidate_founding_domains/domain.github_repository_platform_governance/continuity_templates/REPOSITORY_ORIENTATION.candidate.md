# Repository Orientation — Continuity Template

schema_id: ion.repository_governance.repository_orientation.v0_1_candidate
owner_domain_id: domain.github_repository_platform_governance
posture: read_only_orientation

## Bindings (fill on each orientation pass)

- repository_slug: ION-operations/ION-Production
- primary_remote_url: https://github.com/ION-operations/ION-Production.git
- shell_root: /home/sev/ION - Production/ION_Developement
- git_toplevel: /home/sev/ION - Production/ION_Developement
- active_branch: codex/ion-custom-gpt-front-door-carrier-v4
- branch_class: feature_carrier_lane
- protected_upstream_branches: [main, master]
- observed_at: <ISO8601>
- observer_role: role.github_repository_platform_governance_steward

## Read-only checks (no mutation)

- [ ] Remote URL matches registry candidate record
- [ ] Active branch recorded without checkout
- [ ] Upstream ahead/behind noted if compare receipt exists
- [ ] No credential values in this template

## Relationship feeds

- Identity authority: `domain.context_graph_branch_fabric`
- Platform read model: this domain
- Commit/push authority: **outside** this domain — requires provenance manifest + operator gate

## Non-claims

Candidate orientation only. Not git config authority. No GitHub API mutation.
