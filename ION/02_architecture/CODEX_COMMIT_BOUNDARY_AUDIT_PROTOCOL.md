# Codex Commit Boundary Audit Protocol

Status: candidate protocol for `PCKT-ION-CODEX-COMMIT-BOUNDARY-AUDIT-001`.

Codex CLI/App can produce a mixed dirty tree: source changes, generated carrier projections, branch-capsule records, local-PC evidence, runtime residue, deletion cleanups, and private diagnostic lanes. ION must classify that mixture before staging or committing.

## Rule

```text
Dirty tree is evidence of work, not a commit boundary.
Commit boundary is proposed only after path classification, proof obligations, and settlement review.
```

This protocol does not allow autonomous staging, committing, pushing, accepted-state mutation, production authority, or raw Codex context promotion.

## Bundle classes

| Bundle | Default action |
|---|---|
| `source_protocol_schema_tests` | Candidate for first/primary source commit after focused tests. |
| `generated_projection_or_local_evidence` | Candidate evidence bundle; usually commit or regenerate after source commit. |
| `deletion_review_required` | Separate cleanup/archive packet required. |
| `runtime_residue_exclude` | Exclude by default. |
| `private_or_secret_risk_exclude` | Block and review before any commit. |
| `untracked_review_required` | Owner-surface classification required before staging. |
| `preexisting_dirty_or_unknown` | Do not stage with Codex carrier OS bundle. |

## Required proof

```text
git status --porcelain=v1 --branch
git diff --check
focused pytest for source bundle
path-level secret/risk review
stage manifest proposal
operator/Steward settlement before commit/push
```

## Generated artifacts

```text
ION/05_context/current/codex_carrier/commit_boundary/CODEX_COMMIT_BOUNDARY_AUDIT.json
ION/05_context/current/codex_carrier/commit_boundary/CODEX_COMMIT_STAGE_MANIFEST.candidate.json
```

These artifacts are candidate evidence. They are not receipts and do not establish accepted ION state.

## Security boundary

The audit is path-level by default. It must not read raw `~/.codex` transcripts, memory, credentials, tunnel files, browser profiles, `.env` files, raw private logs, or `.ion_private` raw context snapshots. Secret-like paths block the stage plan until reviewed and redacted or excluded.
