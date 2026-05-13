---
atlas_package: system
system_slug: gnu-gdb
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Scope

## In scope

- **gdb** CLI, **inferior** lifecycle, **symbols**, **break/watch** commands (`DOCUMENTED`, `src-gdb-doc`).  
- **gdbserver** and **remote** protocol themes (`DOCUMENTED`).  
- **GDB/MI** for IDE integration (`DOCUMENTED`).

## Out of scope

- **LLDB** — see **`lldb`** (LLVM debugger; different implementation).  
- **Kernel** **KGDB** — specialized; cite kernel docs if split later (`INFERRED`).

## Versioning note

**GDB** releases; **Python** scripting API evolves (`DOCUMENTED` release notes).
