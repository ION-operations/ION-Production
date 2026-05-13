---
atlas_package: system
system_slug: kubevirt
schema_version: "1.0"
last_reviewed: "2026-04-06"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- Kubernetes extension model and user-guide architecture topics (`kubevirt-001`, `src-kubevirt-user-guide`).

## INFERRED

- Specific libvirt/QEMU command lines for a node without reading that node configuration.

## UNKNOWN

- `kubevirt-003` unless sourced per deployment.

## Forbidden until sourced

- Cloud-managed “KubeVirt inside X” internals without operator documentation.
