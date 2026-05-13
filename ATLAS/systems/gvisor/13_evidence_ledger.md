---
atlas_package: system
system_slug: gvisor
schema_version: "1.0"
last_reviewed: "2026-04-08"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| gvisor-001 | gVisor documents runsc as an OCI-compatible runtime on Linux | DOCUMENTED | `src-gvisor-docs` | |
| gvisor-002 | gVisor is distinct from namespace-only runc and from VM-backed Kata at the mechanism level | INFERRED | — | survey boundary |
| gvisor-003 | Undocumented syscall compatibility for a random binary without testing | UNKNOWN | — | non-claim |
