---
atlas_package: system
system_slug: rust-language
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Ownership**, **borrowing**, **lifetimes**, **Send/Sync** — survey (`DOCUMENTED`, `src-rust-reference`).  
- **std** library and **no_std** — embedded / kernel contexts (`DOCUMENTED`, `src-rust-reference`).  
- **Kernel** adoption narrative — pointer to kernel docs (`DOCUMENTED`, `src-linux-rust-for-linux`).

## Out of scope

- **rustc** MIR optimization passes — **UNKNOWN** without compiler paper.  
- **Unsafe Rust** audit of any specific codebase — **UNKNOWN** here.

## Versioning note

Pin **edition** + **rustc** version for **toolchain** claims (`OBSERVED`).
