---
atlas_package: system
system_slug: llvm-libcxx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# LLVM libc++ — Identity

**Kind:** LLVM **project** **C++** **standard** **library** **implementation** — **headers**, **runtime** **objects**, **Clang** **`-stdlib=libc++`** **path** (`DOCUMENTED`, `src-llvm-libcxx-docs`).

## Boundaries

- **Not** **`clang`** — **compiler** **front** **end** **and** **driver** (`DOCUMENTED`).  
- **Not** **`llvm-lld`** — **linker** **package** (`DOCUMENTED`).  
- **Not** **`gnu-libstdcxx`** — **GCC** **project** **C++** **stdlib** (`DOCUMENTED`).  
- **Not** **`glibc`** / **`musl`** — **C** **libcs** **under** **the** **C++** **runtime** (`DOCUMENTED`).  
- **Not** **`llvm-libcxxabi`** — **low-level** **C++** **ABI** **runtime** **(exceptions,** **RTTI,** …) **is** **a** **separate** **`cxx-abi-runtime`** **package** (`DOCUMENTED`).

## Why this system matters

- **Primary** **C++** **stdlib** **option** **in** **LLVM**/**Clang**-**centric** **toolchains** **when** **`-stdlib=libc++`** **is** **used** (`DOCUMENTED`).  
- **Pairs** **with** **`llvm-lld`** **and** **`lldb`** **in** **many** **cross** **and** **native** **LLVM** **stacks** (`DOCUMENTED`).

## What this system teaches the atlas

**Split** **C++** **stdlib** **from** **compiler** **and** **from** **C** **libc** — **two** **`cxx-runtime`** **grains** **(`gnu-libstdcxx`**, **`llvm-libcxx`)**.
