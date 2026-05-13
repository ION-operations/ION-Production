---
atlas_package: system
system_slug: rust-language
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Architecture (language + toolchain)

## Core semantic model

**Ownership** of values; **borrowing** (`&`, `&mut`); **lifetimes** to relate references to data (`DOCUMENTED`, `src-rust-reference`).

## Type system

**Traits** (similar in spirit to type classes); **generics** with trait bounds (`DOCUMENTED`, `src-rust-reference`).

## Compilation

**rustc** → LLVM IR → machine code; **link** with **C** ABI where `extern "C"` (`DOCUMENTED` pattern).
