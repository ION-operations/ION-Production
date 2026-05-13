---
atlas_package: system
system_slug: gnu-binutils
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Scope

## In scope

- Documented **command-line tools** and their roles (linking, archiving, disassembly, section manipulation) (`DOCUMENTED`, `src-binutils-docs`).  
- **Target support** model (multi-architecture backends) at survey level (`DOCUMENTED` overview).

## Out of scope

- **MSVC** `link.exe` / **PE** toolchain — different stack (`UNKNOWN` here).  
- **Gold** vs **bfd ld** internal design — deep dive unless ledger-pinned.

## Versioning note

Release numbering follows GNU/binutils release practice; distro backports vary (`INFERRED` deployment).
