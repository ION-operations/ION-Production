---
atlas_package: system
system_slug: liburing
schema_version: "1.0"
last_reviewed: "2026-04-17"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| liburing-001 | liburing documents itself as a helper library for Linux io_uring | DOCUMENTED | `src-liburing-github` | |
| liburing-002 | Kernel io_uring documentation references liburing as the userspace library | DOCUMENTED | `src-io-uring-kernel-docs` | |
| liburing-003 | Distinct from raw io_uring syscall programming without helpers | INFERRED | — | survey boundary |
