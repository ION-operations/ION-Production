---
atlas_package: system
system_slug: linux-vhost
schema_version: "1.0"
last_reviewed: "2026-04-28"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| linux-vhost-001 | Kernel drivers/vhost/vhost.c implements the vhost core used for virtio backend acceleration | DOCUMENTED | `src-linux-vhost-kernel-doc` | |
| linux-vhost-002 | vhost is a distinct concern from the virtio guest-visible device contract alone | INFERRED | — | survey boundary |
| linux-vhost-003 | vhost is not interchangeable with the KVM hypervisor API alone | INFERRED | — | survey boundary |
