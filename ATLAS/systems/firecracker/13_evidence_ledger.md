---
atlas_package: system
system_slug: firecracker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| fc-001 | Firecracker is a VMM using KVM | DOCUMENTED | `src-firecracker-getting-started` | |
| fc-002 | Requires `/dev/kvm` access on Linux hosts | DOCUMENTED | `src-firecracker-getting-started` | |
| fc-003 | AWS Lambda internal topology | UNKNOWN | — | Explicit non-claim |
| fc-004 | Designed for lightweight microVMs (minimal device model) | DOCUMENTED | `src-firecracker-docs` | Pin section on upgrade |
