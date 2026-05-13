---
atlas_package: system
system_slug: llvm-libcxxabi
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **libc++abi** **as** **documented** **for** **the** **LLVM** **project** — **ABI** **routines** **consumed** **by** **libc++** **and** **Clang-generated** **code** (`DOCUMENTED`, `src-llvm-libcxxabi-docs`).  
- **Link** **and** **deployment** **alongside** **`llvm-libcxx`** **on** **ELF** **targets** (`DOCUMENTED`).

## Out of scope

- **Full** **C++** **standard** **library** **algorithms** **/** **containers** — **`llvm-libcxx`** (`DOCUMENTED`).  
- **Platform** **C** **API** — **`glibc`** **/** **`musl`** (`DOCUMENTED`).

## Versioning note

**Tracks** **LLVM** **monorepo** **releases** **when** **built** **with** **LLVM** **distributions** (`DOCUMENTED`).
