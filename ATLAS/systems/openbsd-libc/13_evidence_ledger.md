---
atlas_package: system
system_slug: openbsd-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| obsd-libc-001 | OpenBSD documents base system and libc manuals | DOCUMENTED | `src-openbsd-faq` | |
| obsd-libc-002 | libc participates in ELF dynamic linking on OpenBSD | DOCUMENTED | man pages | |
| obsd-libc-003 | Ports builds link against base libc | OBSERVED | ports | field pattern |
