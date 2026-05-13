---
atlas_package: system
system_slug: wasi-libc
schema_version: "1.0"
last_reviewed: "2026-04-13"
evidence_grade: B
---

# wasi-libc — Identity

**Kind:** **C** **standard** **library** **implementation** **for** **WebAssembly** **targets** **using** **the** **WebAssembly** **System** **Interface** (**WASI**), **built** **as** **a** **sysroot** **for** **clang**/**LLVM** **wasm** **toolchains** (`DOCUMENTED`, `src-wasi-libc-github`).

## Boundaries

- **Not** **the** **WASI** **specification** **itself** — **that** **is** **`wasi`** (`DOCUMENTED`).  
- **Not** **core** **WebAssembly** **semantics** — **that** **is** **`webassembly`** (`DOCUMENTED`).  
- **Not** **ABI-interchangeable** **with** **`glibc`**, **`musl`**, **or** **hosted** **Unix** **libcs** — **wasm** **triplets** **and** **import** **models** **differ** (`INFERRED`).

## Why this system matters

- **Default** **C** **library** **story** **for** **`wasm32-wasi`** **and** **related** **LLVM** **targets** **in** **the** **Bytecode** **Alliance**/**LLVM** **ecosystem** (`DOCUMENTED`).

## What this system teaches the atlas

**Separate** **WASI** **the** **API** **surface** **from** **wasi-libc** **the** **buildable** **libc** **sysroot** **when** **auditing** **Wasm** **toolchains**.
