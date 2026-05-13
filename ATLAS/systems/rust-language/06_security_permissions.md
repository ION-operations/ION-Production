---
atlas_package: system
system_slug: rust-language
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Security and permissions

## Memory safety

**Safe Rust** forbids **data races** and **use-after-free** by construction — **`unsafe`** escapes exist (`DOCUMENTED`, `src-rust-reference`).

## Threat model

**Unsafe** and **FFI** reintroduce **C**-class hazards (`DOCUMENTED` language rules; **UNKNOWN** per crate).
