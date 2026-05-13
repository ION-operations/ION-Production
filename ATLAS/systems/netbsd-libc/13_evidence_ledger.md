---
atlas_package: system
system_slug: netbsd-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| nbsd-libc-001 | NetBSD Guide documents base system userland including libc | DOCUMENTED | `src-netbsd-guide` | |
| nbsd-libc-002 | libc participates in ELF dynamic linking on NetBSD | DOCUMENTED | man pages | |
| nbsd-libc-003 | pkgsrc builds link against base libc | OBSERVED | pkgsrc | field pattern |
