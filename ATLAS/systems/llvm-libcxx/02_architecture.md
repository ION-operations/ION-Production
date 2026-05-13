---
atlas_package: system
system_slug: llvm-libcxx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **C++** **standard** **facilities** **implemented** **above** **the** **platform** **C** **library** **and** **compiler** **runtime** (`DOCUMENTED`).

## Link shape

- **`libc++.so`** **/** **static** **archives** **(and** **often** **`libc++abi`)** **resolved** **at** **link** **time** **via** **Clang** **/** **lld** **or** **GNU** **ld** (`DOCUMENTED`).
