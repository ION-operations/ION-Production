---
atlas_package: system
system_slug: dragonfly-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| dfly-libc-001 | DragonFly Handbook documents base system userland including libc | DOCUMENTED | `src-dfly-handbook` | |
| dfly-libc-002 | libc participates in ELF dynamic linking on DragonFly | DOCUMENTED | man pages | |
| dfly-libc-003 | dports builds link against base libc | OBSERVED | dports | field pattern |
