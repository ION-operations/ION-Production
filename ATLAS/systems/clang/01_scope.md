---
atlas_package: system
system_slug: clang
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Scope

## In scope

- **clang** / **clang++** driver behavior, **language modes**, **warning flags** (`DOCUMENTED`, `src-clang-manual`).  
- **Lowering** to LLVM IR for optimization/codegen (`DOCUMENTED`).

## Out of scope

- **libc** choice (**glibc** vs **musl**) — deployment (`INFERRED`).  
- **MSVC** `cl.exe` compatibility flags — acknowledge **`clang-cl`** exists; Windows stack not ATLAS default emphasis.

## Versioning note

Tracks **LLVM** release train (`DOCUMENTED`).
