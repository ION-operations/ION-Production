---
atlas_package: system
system_slug: glibc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| glibc-001 | glibc provides the GNU C Library (ISO C + POSIX/GNU extensions) on typical GNU/Linux systems | DOCUMENTED | `src-glibc-manual` | |
| glibc-002 | Dynamic linker (ld-linux) is part of glibc and participates in ELF program loading | DOCUMENTED | `src-glibc-manual` | |
| glibc-003 | Userland syscall wrappers mediate the boundary to the Linux kernel | DOCUMENTED | `src-glibc-manual`; `linux-kernel` | |
