---
atlas_package: system
system_slug: freebsd-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| fbsd-libc-001 | FreeBSD Handbook documents base system userland including libc | DOCUMENTED | `src-freebsd-handbook-libc` | |
| fbsd-libc-002 | libc participates in ELF dynamic linking on FreeBSD | DOCUMENTED | handbook; man pages | |
| fbsd-libc-003 | Ports toolchains link against base libc | OBSERVED | ports | field pattern |
