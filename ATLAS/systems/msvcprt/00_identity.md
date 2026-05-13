---
atlas_package: system
system_slug: msvcprt
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# MSVC C++ runtime (msvcp*.dll) — Identity

**Kind:** **Microsoft** **Visual** **C++** **C++** **standard** **library** **implementation** **shipped** **as** **`msvcp*.dll`** **(and** **related)** **for** **MSVC**-**ABI** **C++** **binaries** **on** **Windows** (`DOCUMENTED`, `src-ms-learn-cpp-runtime`).

## Boundaries

- **Not** **`gnu-libstdcxx`** **or** **`llvm-libcxx`** — **Windows** **MSVC** **ABI** **/** **DLL** **deployment** (`DOCUMENTED`).  
- **Not** **`msvc-vcruntime`** **(C** **/** **UCRT** **surface)** — **separate** **package** (`DOCUMENTED`).  
- **Not** **the** **C++** **compiler** **front** **end** — **runtime** **DLLs** **only** (`DOCUMENTED`).

## Why this system matters

- **Default** **C++** **stdlib** **runtime** **for** **native** **MSVC** **toolchain** **outputs** **on** **Windows** (`DOCUMENTED`).

## What this system teaches the atlas

**Keep** **Windows** **MSVC** **C++** **runtime** **distinct** **from** **GCC**/**Clang** **libstdc++**/**libc++** **on** **Unix** **when** **mapping** **ABI** **graphs**.
