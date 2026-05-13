---
atlas_package: system
system_slug: gvisor
schema_version: "1.0"
last_reviewed: "2026-04-08"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- runsc OCI runtime positioning and operator documentation topics (`gvisor-001`, `src-gvisor-docs`).

## INFERRED

- Whether a specific proprietary workload is supported without compatibility testing.

## UNKNOWN

- `gvisor-003` unless sourced per workload.

## Forbidden until sourced

- “Stronger than Kata/runc” security claims without cited threat model and benchmark protocol.
