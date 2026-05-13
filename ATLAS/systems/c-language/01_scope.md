---
atlas_package: system
system_slug: c-language
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Syntax** categories (declarations, statements, preprocessor), **memory** model (`malloc`/`free`), **UB** concept — survey (`DOCUMENTED`, `src-wiki-c`).  
- **Standard library** roles (`stdio`, `stdlib`, `string`, …) — overview (`DOCUMENTED`, `src-wiki-c`).  
- **Linkage** to **kernels** and **FFI** — pattern level.

## Out of scope

- **Compiler** SSA internals — **UNKNOWN** in this package.  
- **MISRA C** / **CERT C** — add **separate** ledger rows if expanded.

## Versioning note

Pin **ISO** year for **standard-math** or **threads** (`threads.h`) claims (`DOCUMENTED` per edition).
