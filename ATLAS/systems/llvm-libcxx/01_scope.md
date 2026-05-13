---
atlas_package: system
system_slug: llvm-libcxx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **libc++** **as** **documented** **on** **libcxx.llvm.org** — **headers**, **link** **model**, **Clang** **integration** (`DOCUMENTED`, `src-llvm-libcxx-docs`).  
- **Deployment** **with** **`clang`**, **`llvm-lld`**, **and** **platform** **C** **libraries** **on** **ELF** **targets** (`DOCUMENTED` / `INFERRED`).

## Out of scope

- **`llvm-libcxxabi`** **detail** — **see** **`llvm-libcxxabi/`** (`DOCUMENTED`).  
- **Full** **ISO** **C++** **normative** **text** — **`c-language`** **adjacency** **for** **interop** **only** (`INFERRED`).

## Versioning note

**libc++** **release** **tracks** **LLVM** **cadence** **when** **shipped** **with** **LLVM** **distributions** (`DOCUMENTED`).
