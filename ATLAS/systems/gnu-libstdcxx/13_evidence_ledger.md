---
atlas_package: system
system_slug: gnu-libstdcxx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| lsx-001 | GNU libstdc++ is the C++ standard library implementation shipped with GCC | DOCUMENTED | `src-libstdcxx-manual` | |
| lsx-002 | libstdc++ depends on a C library (e.g. glibc) for many underlying POSIX/C services | DOCUMENTED | `src-libstdcxx-manual`; `glibc` | |
| lsx-003 | Typical g++ links add libstdc++ alongside object files and libc | DOCUMENTED | GCC docs; `gnu-gcc` | |
