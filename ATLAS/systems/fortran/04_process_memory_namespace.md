---
atlas_package: system
system_slug: fortran
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Process, memory, and namespace

## Scoping

**Modules** provide **symbol** namespaces in modern Fortran; **USE**/`ONLY` control visibility (`DOCUMENTED`, `src-wiki-fortran`).

## Storage

**STATIC**, **STACK**, **HEAP** (`ALLOCATABLE`) — model depends on **standard** + **compiler** (`DOCUMENTED` overview; **UNKNOWN** per implementation detail).
