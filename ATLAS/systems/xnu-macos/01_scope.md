---
atlas_package: system
system_slug: xnu-macos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Scope

## In scope

- Public Apple OSS XNU sources and high-level kernel programming documentation (`DOCUMENTED`).  
- Syscall/interface class comparisons at documented abstraction levels.

## Out of scope

- Undisclosed Apple Silicon firmware or Secure Enclave internals — **UNKNOWN**.  
- Detailed windowing system.

## Versioning note

macOS major versions track XNU versions; cite version for precise syscall or KPI claims (`DOCUMENTED` pattern).
