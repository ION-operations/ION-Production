---
atlas_package: system
system_slug: llvm-lld
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# LLVM lld

**Kind:** **LLVM** **project** **linker** (**lld**) — drop-in style replacement for platform linkers on many targets, consuming relocatable objects and emitting **ELF** / **Mach-O** / **COFF** / **Wasm** outputs depending on build and flags (`DOCUMENTED`, `src-lld-home`, `src-lld-cg`).

## Boundaries

- **Not** **GNU ld** — different implementation; often selected via **`-fuse-ld=lld`** or toolchain defaults (`DOCUMENTED` Clang docs themes).  
- **Not** the **ELF** specification — **consumes** ELF objects on Unix-class targets (`DOCUMENTED`; see `elf`).  
- **Not** a full **GNU Binutils** replacement — **no** GNU **as** equivalent in this package (`DOCUMENTED` scope).

## Why this system matters

- **Faster** / **simpler** linking path in **Clang** / **Rust** heavy stacks (`DOCUMENTED` project claims + adoption).  
- Clarifies **competition** at the **link** stage vs **`gnu-binutils`** **ld** (`INFERRED` deployment class).

## What this system teaches the atlas

- Keep **linker choice** (`llvm-lld` vs **GNU ld**) explicit when describing “the” toolchain.
