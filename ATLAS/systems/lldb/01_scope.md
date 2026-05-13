---
atlas_package: system
system_slug: lldb
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Scope

## In scope

- **lldb** command interpreter, **breakpoints**, **expressions**, **memory** inspection (`DOCUMENTED`, `src-lldb-use`).  
- **SB API** / Python scripting (`DOCUMENTED`).  
- **Remote** debugging themes (`DOCUMENTED`).

## Out of scope

- **lldb-server** packaging details per vendor — survey (`INFERRED`).  
- **Windows** COFF/PDB combinations — acknowledge multi-target; ELF focus is default ATLAS emphasis.

## Versioning note

Tracks **LLVM** release train (`DOCUMENTED`).
