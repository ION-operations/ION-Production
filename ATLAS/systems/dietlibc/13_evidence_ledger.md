---
atlas_package: system
system_slug: dietlibc
schema_version: "1.0"
last_reviewed: "2026-04-15"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| dietlibc-001 | dietlibc documents itself as a libc for Linux with emphasis on small static binaries | DOCUMENTED | `src-dietlibc-fefe` | |
| dietlibc-002 | diet wrapper integrates GCC with dietlibc for compile/link | DOCUMENTED | `src-dietlibc-fefe` | |
| dietlibc-003 | Not ABI-interchangeable with glibc or musl for arbitrary binaries | INFERRED | — | survey boundary |
