---
atlas_package: system
system_slug: llvm-lld
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Scope

## In scope

- **lld** as LLVM’s linker subproject: supported formats and **driver** behavior (`DOCUMENTED`, `src-lld-cg`).  
- Relationship to **clang** as **link driver** (`DOCUMENTED`).

## Out of scope

- **Linker scripts** / **LTO** deep internals — survey only unless ledger-pinned.  
- **PE**/**COFF** Windows details — acknowledge multi-target nature; Unix ELF focus is default ATLAS emphasis.

## Versioning note

Releases track **LLVM** release train (`DOCUMENTED`).
