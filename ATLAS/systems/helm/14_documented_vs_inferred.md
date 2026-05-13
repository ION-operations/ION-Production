---
atlas_package: system
system_slug: helm
schema_version: "1.0"
last_reviewed: "2026-04-10"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Helm positioning and Kubernetes API usage (`helm-001`, `src-helm-docs`).

## INFERRED

- Whether a specific GitOps controller replaces Helm entirely in a given org.

## UNKNOWN

- `helm-003` unless chart provenance and supply-chain review is cited.

## Forbidden until sourced

- “Helm is secure by default” without RBAC, chart provenance, and registry policy context.
