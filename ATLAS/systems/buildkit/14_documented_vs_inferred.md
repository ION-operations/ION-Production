---
atlas_package: system
system_slug: buildkit
schema_version: "1.0"
last_reviewed: "2026-04-09"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- BuildKit positioning in Docker build documentation and moby/buildkit README/overview (`buildkit-001`, `src-buildkit-docs`).

## INFERRED

- Whether a specific regulated environment may run privileged builders on production nodes.

## UNKNOWN

- `buildkit-003` unless build logs and lockfiles are cited per pipeline.

## Forbidden until sourced

- “Reproducible builds” marketing claims without cited base-image digests and cache keys.
