---
atlas_package: system
system_slug: linux-netfilter
schema_version: "1.0"
last_reviewed: "2026-04-24"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| linux-netfilter-001 | Kernel netfilter documentation describes the netfilter subsystem and hook framework | DOCUMENTED | `src-linux-netfilter-kernel-docs` | |
| linux-netfilter-002 | Netfilter is a distinct concern from eBPF-based datapaths (e.g. some CNI modes) at the architectural level | INFERRED | — | survey boundary |
| linux-netfilter-003 | Netfilter is not interchangeable with L7 reverse proxies or with OCI runtime isolation | INFERRED | — | survey boundary |
