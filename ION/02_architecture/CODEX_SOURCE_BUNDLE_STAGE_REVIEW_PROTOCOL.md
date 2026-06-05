# Codex Source Bundle Stage Review Protocol

Status: candidate protocol for `PCKT-ION-CODEX-SOURCE-BUNDLE-STAGE-REVIEW-003`.

The commit-boundary audit classifies the dirty tree. This protocol turns that classification into the first safe source/protocol/schema/test stage proposal without staging, committing, pushing, settling, or promoting generated/local evidence.

## Rule

```text
A source bundle may be proposed only after the dirty tree has been classified.
The proposal may include source/protocol/schema/test paths only.
Generated projections, local evidence, runtime residue, raw context, unknown owner paths, and deletion cleanup do not ride with the first source commit.
```

This protocol produces a stage review and a candidate source-bundle stage manifest. Both are proposals. They do not mutate Git and do not create accepted ION state.

## Inputs

```text
ION/05_context/current/codex_carrier/commit_boundary/CODEX_COMMIT_BOUNDARY_AUDIT.json
ION/05_context/current/codex_carrier/commit_boundary/CODEX_COMMIT_STAGE_MANIFEST.candidate.json
or a live read-only execution of kernel.ion_codex_commit_boundary_audit
```

## Outputs

```text
ION/05_context/current/codex_carrier/commit_boundary/CODEX_SOURCE_BUNDLE_STAGE_REVIEW.json
ION/05_context/current/codex_carrier/commit_boundary/CODEX_SOURCE_BUNDLE_STAGE_MANIFEST.candidate.json
```

## Inclusion rule

Only paths classified as `source_protocol_schema_tests` may enter the first source-bundle stage proposal.

Typical included surfaces:

```text
.codex/**
ION/02_architecture/**
ION/03_registry/**
ION/04_packages/kernel/**
ION/07_templates/**
ION/tests/**
.gitignore
README.md
CONTRIBUTING.md
SECURITY.md
pyproject.toml
```

## Exclusion rule

The first source bundle must exclude:

```text
ION/05_context/current/** generated projections and local evidence
ION/05_context/current/** branch capsule runtime/evidence records
.ion_private/** raw Codex context snapshots
runtime/** bridge/service residues
unknown owner-surface paths
private/secret-risk paths
deletions without a cleanup/archive packet
```

## Required proof before actual staging

```text
git status --porcelain=v1 --branch -uall
git diff --check
focused pytest for touched kernel/protocol/schema/test paths
secret/path review for source paths
operator review of excluded generated/evidence/runtime/unknown groups
explicit human/Codex command to stage, after this proposal is reviewed
```

## Authority boundary

```text
source stage review = proposal
Git staging = separate human/operator-approved action
Git commit = separate proof-bearing action
push/PR = separate policy-gated action
receipt/settlement = ION acceptance path
```

Non-claims:

```text
No accepted ION state.
No production authority.
No live execution authority.
No secrets authority.
No Git mutation.
No GitHub mutation.
No raw Codex context promotion.
```
