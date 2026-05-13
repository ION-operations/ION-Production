---
atlas_package: system
system_slug: virtio
schema_version: "1.0"
last_reviewed: "2026-04-27"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| virtio-001 | Kernel virtio documentation describes virtio queues, descriptors, and the Linux driver model | DOCUMENTED | `src-virtio-kernel-docs` | |
| virtio-002 | Virtio is a distinct concern from the KVM hypervisor API alone | INFERRED | — | survey boundary |
| virtio-003 | Virtio is not interchangeable with a specific VMM product (e.g. Firecracker) by itself | INFERRED | — | survey boundary |
