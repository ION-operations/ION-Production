---
atlas_package: system
system_slug: linux-vfio
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| linux-vfio-001 | Kernel VFIO driver API is documented in the mainline kernel docs (device assignment, IOMMU groups, userspace interface) | DOCUMENTED | `src-linux-vfio-kernel-doc` | |
| linux-vfio-002 | VFIO is a distinct concern from virtio paravirtual device negotiation alone | INFERRED | — | survey boundary |
| linux-vfio-003 | VFIO is not interchangeable with the KVM `/dev/kvm` hypervisor API alone | INFERRED | — | survey boundary |
