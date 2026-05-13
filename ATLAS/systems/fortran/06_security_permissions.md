---
atlas_package: system
system_slug: fortran
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Security and permissions

## Memory safety

**Bounds checking** is **optional** or **compiler-flag** dependent — not Rust-like guarantees by default (`DOCUMENTED` compiler-typical; **UNKNOWN** per flag without manual).

## Sandboxing

**OS** responsibility — Fortran runtime does not provide a browser-style sandbox (`INFERRED`).
