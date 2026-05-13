---
atlas_package: system
system_slug: linux-cgroups
schema_version: "1.0"
last_reviewed: "2026-04-21"
evidence_grade: B
---

# Scope

## In scope

- **cgroup** **v2** **controller** **model** **and** **documented** **filesystem** **/** **API** **usage** (`DOCUMENTED`).  
- **Relationship** **to** **systemd** **/** **container** **runtimes** **as** **integration** **patterns** (`INFERRED`).

## Out of scope

- **Legacy** **cgroup** **v1** **only** **deployments** — **historical** **survey** **unless** **promoted** **as** **separate** **ledger** **work**.  
- **Non-Linux** — **out** **of** **package**.

## Versioning note

**Controller** **sets** **and** **defaults** **evolve** **with** **kernel** **and** **distribution** **policy** (`OBSERVED`).
