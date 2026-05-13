---
atlas_package: system
system_slug: linux-capabilities
schema_version: "1.0"
last_reviewed: "2026-04-22"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| linux-capabilities-001 | capabilities(7) documents capability sets and the splitting of traditional superuser privileges | DOCUMENTED | `src-linux-capabilities-man7` | |
| linux-capabilities-002 | Capabilities are a distinct concern from Linux namespaces (visibility) and cgroups (resources) | INFERRED | — | survey boundary |
| linux-capabilities-003 | Capabilities are not interchangeable with seccomp syscall filtering or with LSM MAC policy alone | INFERRED | — | survey boundary |
