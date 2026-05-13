---
atlas_package: system
system_slug: landlock
schema_version: "1.0"
last_reviewed: "2026-04-18"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| landlock-001 | Kernel docs describe Landlock as an LSM for unprivileged sandboxing with a userspace syscall ABI | DOCUMENTED | `src-landlock-kernel-docs` | |
| landlock-002 | Landlock project materials position it as filesystem access control without traditional MAC policy languages | DOCUMENTED | `src-landlock-io` | |
| landlock-003 | Distinct from “all of LSM” as a single umbrella package | INFERRED | — | survey boundary |
