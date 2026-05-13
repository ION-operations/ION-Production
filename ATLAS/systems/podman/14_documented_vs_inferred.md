---
atlas_package: system
system_slug: podman
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Documented vs inferred

## DOCUMENTED

- Daemonless default; rootless (`pdm-001`, `pdm-002`); compatibility caveats (`pdm-003`).

## INFERRED

- Kubernetes adjacency via local dev flows.

## Forbidden until sourced

- “Drop-in replacement for Docker in all CI systems” — environment-specific.
