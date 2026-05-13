---
atlas_package: system
system_slug: linux-fuse
schema_version: "1.0"
last_reviewed: "2026-04-25"
evidence_grade: B
---

# Scope

## In scope

- **Kernel** **FUSE** **architecture** **and** **documented** **interfaces** (`DOCUMENTED`).  
- **Typical** **userspace** **daemon** **patterns** **(e.g.** **libfuse-based)** **as** **integration** **context** (`INFERRED`).  
- **Mount** **namespace** **interaction** **for** **FUSE** **mounts** (`INFERRED`).

## Out of scope

- **Per-distribution** **FUSE** **default** **limits** **(max** **pages,** **congestion)** **—** **consult** **kernel** **and** **distro** **docs** **unless** **promoted** **to** **ledger** **rows.**  
- **Non-Linux** **FUSE-like** **facilities** **—** **out** **unless** **scoped** **later.**

## Versioning note

**Protocol** **and** **feature** **bits** **evolve** **with** **kernel** **releases** (`OBSERVED`).
