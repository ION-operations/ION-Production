---
atlas_package: system
system_slug: clang
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Clang

**Kind:** **LLVM** **C/C++/Objective-C** **compiler front end** and **`clang`** **driver** — parses those languages, lowers to **LLVM IR**, invokes the **system linker** (often **GNU ld** or **lld**) (`DOCUMENTED`, `src-clang-home`, `src-clang-manual`).

## Boundaries

- **Not** **LLVM IR** semantics — IR definition is **`llvm-ir`** (`DOCUMENTED`).  
- **Not** the **linker** — **`llvm-lld`** or **`gnu-binutils`** **ld** (`DOCUMENTED` driver split).  
- **Not** **GCC** — different front end and driver; both compile **`c-language`**-family sources (`DOCUMENTED` comparative).

## Why this system matters

- Default **LLVM** path for **C/C++** on many platforms; drives **`-fuse-ld=lld`** adoption (`DOCUMENTED`).  
- **Sanitizers** / **static analyzer** ecosystem centers on Clang (`DOCUMENTED` manual sections).

## What this system teaches the atlas

- Split **front end + driver** (`clang`) from **IR** (`llvm-ir`) and **linker** (`llvm-lld` / **GNU ld**).
