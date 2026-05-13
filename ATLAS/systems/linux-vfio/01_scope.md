---
atlas_package: system
system_slug: linux-vfio
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Kernel** **VFIO** **driver** **model,** **IOMMU** **groups,** **and** **documented** **userspace** **interfaces** (`DOCUMENTED`).  
- **Composition** **with** **KVM** **and** **VMM-class** **stacks** **for** **device** **passthrough** (`INFERRED`).  
- **Contrast** **with** **paravirtual** **virtio** **paths** **at** **survey** **grain** (`INFERRED`).

## Out of scope

- **Per-vendor** **PCIe** **ACS** **errata** **matrices** **—** **use** **hardware** **/** **platform** **docs.**  
- **Full** **QEMU** **command-line** **catalog** **for** **every** **passthrough** **device** **class** **—** **unless** **QEMU** **is** **a** **separate** **package.**

## Versioning note

**VFIO** **and** **IOMMU** **subsystems** **evolve** **across** **kernel** **releases** (`OBSERVED`).
