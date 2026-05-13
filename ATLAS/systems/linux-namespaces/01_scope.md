---
atlas_package: system
system_slug: linux-namespaces
schema_version: "1.0"
last_reviewed: "2026-04-20"
evidence_grade: B
---

# Scope

## In scope

- **Namespace** **types** **and** **documented** **APIs** **for** **creating** **and** **joining** **namespaces** (`DOCUMENTED`).  
- **Interaction** **patterns** **with** **capabilities** **and** **user** **namespaces** **as** **documented** (`DOCUMENTED` / `INFERRED`).

## Out of scope

- **Full** **cgroup** **v2** **resource** **control** **as** **its** **own** **package** — **optional** **future** **slug**.  
- **Non-Linux** **kernels** — **out** **of** **package**.

## Versioning note

**New** **namespace** **types** **and** **flags** **land** **with** **kernel** **releases** (`OBSERVED`).
