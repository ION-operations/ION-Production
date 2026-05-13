---
atlas_package: system
system_slug: firecracker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- KVM VMM; `/dev/kvm` requirement (`fc-001`, `fc-002`); microVM positioning (`fc-004`).

## UNKNOWN

- `fc-003` cloud internals.

## INFERRED

- Kubernetes-adjacent integrations; “vs containers” substitution framing.

## Forbidden until sourced

- Exact numeric density claims without cited benchmark protocol.
