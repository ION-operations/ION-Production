# Platform Change Receipt — Continuity Template

schema_id: ion.repository_governance.platform_change_receipt.v0_1_candidate
owner_domain_id: domain.github_repository_platform_governance

## When to emit

Record any **proposed** GitHub platform setting change (branch protection, ruleset, Actions policy, CODEOWNERS apply, repository settings) before operator gate or API execution.

## Receipt fields

```yaml
receipt_id: <ISO8601>_<short_slug>
repository_slug: ION-operations/ION-Production
change_class: [branch_protection|ruleset|actions|codeowners|repo_settings|release]
proposal_path: <path to proposal artifact>
operator_gate_required: true
nemesis_review_required: true
git_mutation_required: false
executed: false
executed_at: null
non_claims:
  - candidate_only
  - proposal_not_apply
```

## Authority ladder reminder

Local commit/push remain **outside** this domain. Platform receipts cover GitHub-side proposals only.

## Non-claims

Receipt records intent, not accepted platform state.
