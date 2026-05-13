---
atlas_package: system
system_slug: uclibc
schema_version: "1.0"
last_reviewed: "2026-04-14"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| uclibc-001 | uClibc-ng documents itself as a small C library for Linux | DOCUMENTED | `src-uclibc-ng` | |
| uclibc-002 | Embedded build systems offer uClibc as a libc choice | OBSERVED | Buildroot/OpenWrt docs | |
| uclibc-003 | Not ABI-interchangeable with glibc or musl on arbitrary binaries | INFERRED | — | survey boundary |
