---
atlas_package: system
system_slug: fluxcd
schema_version: "1.0"
last_reviewed: "2026-04-11"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Flux component model and Helm integration (`fluxcd-001`, `src-fluxcd-docs`).

## INFERRED

- Whether a given org replaces Flux with another GitOps controller wholesale.

## UNKNOWN

- `fluxcd-003` unless supply-chain and RBAC review is cited.

## Forbidden until sourced

- “GitOps guarantees cluster security” without cluster RBAC, repo access control, and image provenance context.
