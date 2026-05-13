---
atlas_package: system
system_slug: qemu
schema_version: "1.0"
last_reviewed: "2026-04-04"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| qemu-001 | QEMU documents KVM acceleration on Linux hosts | DOCUMENTED | `src-qemu-docs-master` | |
| qemu-002 | QEMU is a userspace VMM / emulator distinct from the kernel KVM API alone | INFERRED | — | survey boundary |
| qemu-003 | Exact performance of a specific virtio-net setup without that invocation | UNKNOWN | — | non-claim unless benchmark protocol is ledgered |
