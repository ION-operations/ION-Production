---
atlas_package: system
system_slug: illumos-libc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| illum-libc-001 | illumos developer guide documents core OS libraries and libc context | DOCUMENTED | `src-illumos-dev-guide` | |
| illum-libc-002 | libc participates in ELF dynamic linking on illumos | DOCUMENTED | man pages | |
| illum-libc-003 | Distribution packages build and link against base libc | OBSERVED | IPS/pkgsrc per distro | field pattern |
