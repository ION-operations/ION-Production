---
atlas_package: system
system_slug: gnu-libstdcxx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **libstdc++** as **documented** in **GCC** **online** **docs** — **headers**, **ABI**, **dual** **ABI** themes (`DOCUMENTED`, `src-libstdcxx-manual`).  
- **Relationship** to **g++** **driver** and **GCC** **release** **train** (`DOCUMENTED`).

## Out of scope

- **`llvm-libcxx`** **detail** **beyond** **this** **package** — **see** **`llvm-libcxx/`**.  
- **Full** **ISO** **C++** **wording** — **`c-language`** **adjacency** only for **interop** (`INFERRED`).  
- **Kernel** **C++** — **`linux-kernel`** is **mostly** **C** (`INFERRED`).

## Versioning note

**libstdc++** **soname** / **ABI** **pin** **tracks** **GCC** **packaging** (`INFERRED`).
