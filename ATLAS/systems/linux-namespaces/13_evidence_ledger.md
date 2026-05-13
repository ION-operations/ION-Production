---
atlas_package: system
system_slug: linux-namespaces
schema_version: "1.0"
last_reviewed: "2026-04-20"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| linux-namespaces-001 | namespaces(7) documents Linux namespace types and clone/unshare/setns usage | DOCUMENTED | `src-linux-namespaces-man7` | |
| linux-namespaces-002 | Namespaces are often composed with cgroups and seccomp in container stacks — not the same abstraction | INFERRED | — | survey boundary |
| linux-namespaces-003 | Distinct from a specific OCI runtime implementation | INFERRED | — | survey boundary |
