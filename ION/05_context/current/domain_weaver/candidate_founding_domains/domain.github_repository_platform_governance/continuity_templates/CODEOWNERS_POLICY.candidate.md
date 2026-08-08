# CODEOWNERS Policy — Continuity Template

schema_id: ion.repository_governance.codeowners_policy.v0_1_candidate
owner_domain_id: domain.github_repository_platform_governance
status: proposal_shell
repository_slug: ION-operations/ION-Production

## Purpose

Proposal shell for CODEOWNERS mapping on `ION-operations/ION-Production`. Platform domain owns the **policy proposal**; path ownership cartography remains with `domain.context_graph_branch_fabric` and provenance with `domain.artifact_provenance_and_gate_legitimacy`.

## Proposal output path

`ION/05_context/current/repository_governance/CODEOWNERS_PROPOSAL.candidate.md`

## Draft sections (to populate in phase-2 read-model packet)

```text
# CODEOWNERS proposal (candidate)

# ION kernel and templates
/ION/04_packages/          @ION-operations/kernel-maintainers
/ION/07_templates/         @ION-operations/template-curators

# Domain weaver and context
/ION/05_context/           @ION-operations/context-stewards

# Default
*                          @ION-operations/ion-core
```

## Gates before apply

- Tier inventory complete (`BLK-WORKING-TREE-UNCLASSIFIED` closed)
- Forensic hold cleared (`BLK-REBASE12-FORENSIC`)
- Operator review of team handles

## Non-claims

Proposal only. No CODEOWNERS file write in candidate activation. No GitHub team mutation.
