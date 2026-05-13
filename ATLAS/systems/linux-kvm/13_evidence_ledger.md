---
atlas_package: system
system_slug: linux-kvm
schema_version: "1.0"
last_reviewed: "2026-04-26"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| linux-kvm-001 | Kernel KVM documentation describes the KVM subsystem and userspace-facing virtualization model | DOCUMENTED | `src-linux-kvm-kernel-docs` | |
| linux-kvm-002 | KVM-based virtualization is a distinct isolation boundary from Linux namespaces/cgroups containers | INFERRED | — | survey boundary |
| linux-kvm-003 | KVM is not interchangeable with container engines (e.g. Docker) or with a specific VMM product alone | INFERRED | — | survey boundary |
