---
atlas_package: system
system_slug: glibc
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Thin** **syscall** **wrappers** upward to **stdio**, **pthread**, **malloc**, **DNS**/**NSS**, … (`DOCUMENTED` manual structure).

## Loader

- **`ld.so`** / **`ld-linux`** participates in **ELF** **program** **interpreter** and **shared** **library** **resolution** (`DOCUMENTED`).

## Host

- Assumes a **Linux** **kernel** **ABI** on **GNU/Linux** (`DOCUMENTED`).
