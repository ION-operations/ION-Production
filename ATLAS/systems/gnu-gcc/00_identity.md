---
atlas_package: system
system_slug: gnu-gcc
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# GNU Compiler Collection (GCC)

**Kind:** **GNU** **compiler** **suite** — **`gcc`** / **`g++`** drivers, language front ends (C, C++, Fortran, Ada, Go frontend history, …), optimizers, and **machine code** generators that typically invoke **GNU as** and **GNU ld** from **`gnu-binutils`** (`DOCUMENTED`, `src-gcc-home`, `src-gcc-manual`).

## Boundaries

- **Not** **GNU Binutils** — **as**/**ld**/**readelf** are **`gnu-binutils`**; GCC **invokes** them (`DOCUMENTED`).  
- **Not** **Clang** — different implementation; both compile **`c-language`**-family sources (`DOCUMENTED` comparative).  
- **Not** **LLVM IR** as the primary IL — GCC uses **GIMPLE**/RTL-class internals (documented in GCC internals); do not equate with **`llvm-ir`**.

## Why this system matters

- Historical and current **default** C/C++ compiler on many **Linux** distributions and **embedded** cross-compilation SDKs (`DOCUMENTED` + `OBSERVED`).  
- **Linux kernel** traditionally compiled with **GCC** (`DOCUMENTED` build docs).

## What this system teaches the atlas

- Keep **compiler** (`gnu-gcc`), **binutils** (`gnu-binutils`), **format** (`elf`), and **debug info** (`dwarf`) as separate packages with explicit edges.
