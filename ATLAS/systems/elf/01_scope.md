---
atlas_package: system
system_slug: elf
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Scope

## In scope

- ELF **file layout**: header, `e_type` / `e_machine`, section header table, program headers (`DOCUMENTED`, `src-tis-elf`).  
- **Relocations**, **symbols**, **dynamic linking** tags (`DOCUMENTED`, `src-sysv-gabi` themes).  
- 32-bit vs 64-bit ELF class (`DOCUMENTED`).

## Out of scope

- **PE/COFF** (Windows) — different container (`UNKNOWN` in this package).  
- **Per-ISA psABI** manuals (calling convention detail) — cite ISA / OS ABI packages unless ledger-pinned here.

## Versioning note

Toolchains and kernels target **de-facto** ELF extensions; treat vendor/psABI docs as **adjacent** evidence (`INFERRED` unless pinned).
