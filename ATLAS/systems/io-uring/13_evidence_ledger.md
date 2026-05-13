---
atlas_package: system
system_slug: io-uring
schema_version: "1.0"
last_reviewed: "2026-04-17"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| io-uring-001 | Kernel docs describe io_uring as an asynchronous I/O interface with submission/completion queues | DOCUMENTED | `src-io-uring-kernel-docs` | |
| io-uring-002 | io_uring is distinct from legacy Linux AIO and from poll/select-only models in documented comparisons | DOCUMENTED | `src-io-uring-kernel-docs` | |
| io-uring-003 | io_uring is not the same abstraction as epoll for every workload | INFERRED | — | survey boundary |
