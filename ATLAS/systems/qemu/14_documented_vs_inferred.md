---
atlas_package: system
system_slug: qemu
schema_version: "1.0"
last_reviewed: "2026-04-04"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

- KVM acceleration and core QEMU documentation (`qemu-001`, `src-qemu-docs-master`).

## INFERRED

- Typical integration with virtio, vhost, and VFIO on Linux without a specific machine XML or CLI.

## UNKNOWN

- `qemu-003` unless sourced per environment.

## Forbidden until sourced

- Vendor-specific cloud images’ exact QEMU defaults without reading that image definition.
