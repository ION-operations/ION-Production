---
atlas_package: system
system_slug: c-language
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# C — Identity

**Kind:** **Imperative, procedural** programming language with **minimal runtime**, **manual memory** discipline, and **ABI** centrality to **Unix**, **kernels**, and **embedded** stacks (`DOCUMENTED`, `src-wiki-c`).

**Standards:** **ANSI C** (C89/C90), **C99**, **C11**, **C17**, **C23** — ISO/IEC 9899 family (`DOCUMENTED`, `src-wiki-c`).

## Boundaries

- **Not** **C++** — distinct language (future package).  
- **Not** a single **implementation** — GCC, Clang, MSVC, etc. (`DOCUMENTED`).

## Why this system matters

- **Lingua franca** for **OS kernels** (e.g. Linux), **drivers**, **embedded**, **FFI** boundaries (`DOCUMENTED`, `src-wiki-c`).  
- **ABI** and **calling conventions** anchor interoperability with **Fortran** (`ISO_C_BINDING`) and others (`DOCUMENTED`).

## What this system teaches the atlas

- **Undefined behavior** as a **language-design** fact with **security** consequences (`DOCUMENTED`, `src-wiki-c`).
