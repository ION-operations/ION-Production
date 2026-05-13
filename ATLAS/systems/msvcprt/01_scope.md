---
atlas_package: system
system_slug: msvcprt
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **`msvcp*.dll`** **family** **as** **documented** **C++** **stdlib** **runtime** **surface** (`DOCUMENTED`).  
- **Redistributable** **packaging** **with** **VC++** **runtime** **(`DOCUMENTED`).

## Out of scope

- **Clang** **with** **libc++** **on** **Windows** — **use** **`llvm-libcxx`** (`DOCUMENTED`).

## Versioning note

**DLL** **names** **track** **MSVC** **toolset** **versions** **per** **Visual** **Studio** **release** **notes** (`DOCUMENTED`).
