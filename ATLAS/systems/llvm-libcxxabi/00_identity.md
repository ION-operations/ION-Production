---
atlas_package: system
system_slug: llvm-libcxxabi
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# LLVM libc++abi — Identity

**Kind:** LLVM **project** **implementation** **of** **the** **Itanium** **C++** **ABI** **facilities** — **exceptions**, **RTTI**, **static** **destructors**, **dynamic** **cast** **support** — **linked** **with** **`llvm-libcxx`** **on** **typical** **Clang** **stacks** (`DOCUMENTED`, `src-llvm-libcxxabi-docs`).

## Boundaries

- **Not** **`llvm-libcxx`** — **that** **package** **is** **the** **C++** **standard** **library** **headers** **and** **high-level** **runtime** (`DOCUMENTED`).  
- **Not** **`clang`** **or** **`llvm-lld`** — **compiler** **and** **linker** (`DOCUMENTED`).  
- **Not** **`gnu-libstdcxx`** — **GCC** **keeps** **C++** **ABI** **machinery** **folded** **into** **the** **libstdc++** **/** **compiler** **story** **rather** **than** **this** **LLVM** **split** (`INFERRED`).

## Why this system matters

- **Missing** **or** **mismatched** **libc++abi** **breaks** **exception** **propagation** **and** **dynamic** **cast** **at** **link** **or** **run** **time** (`DOCUMENTED` themes).  
- **Completes** **the** **LLVM** **C++** **runtime** **layering** **next** **to** **`llvm-libcxx`** (`DOCUMENTED`).

## What this system teaches the atlas

**Split** **C++** **stdlib** **(`cxx-runtime`)** **from** **low-level** **C++** **ABI** **runtime** **(`cxx-abi-runtime`)** **when** **vendors** **ship** **them** **as** **separate** **`.so`** **artifacts**.
