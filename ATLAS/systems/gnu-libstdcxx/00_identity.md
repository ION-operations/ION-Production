---
atlas_package: system
system_slug: gnu-libstdcxx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# GNU libstdc++ — Identity

**Kind:** **GNU** implementation of the **ISO C++** **standard** **library** shipped and versioned with **GCC** — **containers**, **iostreams**, **STL** algorithms, **ABI** **tags** (`DOCUMENTED`, `src-libstdcxx-manual`).

## Boundaries

- **Not** **`gnu-gcc`** — **g++** **invokes** **GCC**; **libstdc++** is the **runtime** **library** **linked** into C++ programs (`DOCUMENTED`).  
- **Not** **`glibc`** / **`musl`** — those are **C** **libcs**; **libstdc++** **builds** **on** **top** of a **C** **ABI** (`DOCUMENTED`).  
- **Not** **`llvm-libcxx`** — LLVM **project** **libc++** is a **separate** **`cxx-runtime`** (`DOCUMENTED`).  
- **Not** **`elf`** — **shared** **objects** are **ELF**-**shaped** on **typical** **Linux** (`DOCUMENTED` split).

## Why this system matters

- **Default** **C++** **stdlib** on **many** **GNU/Linux** **distros** when **using** **g++** (`DOCUMENTED`).  
- **ABI** **tags** (**`__cxx11`**, …) and **`-std=`** **interactions** drive **link** **errors** in **mixed** **builds** (`DOCUMENTED` manual themes).

## What this system teaches the atlas

- Separate **C++** **stdlib** from **C** **libc** and from **compiler** **driver** when auditing **containers** and **toolchains**.
