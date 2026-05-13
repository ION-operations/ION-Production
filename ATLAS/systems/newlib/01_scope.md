---
atlas_package: system
system_slug: newlib
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **newlib** **as** **the** **portable** **C** **library** **used** **by** **GCC** **for** **embedded** **targets** (`DOCUMENTED`).  
- **Startup** **/** **syscall** **stub** **models** **as** **documented** **for** **BSP** **integration** (`DOCUMENTED` **/** `INFERRED`).

## Out of scope

- **Vendor** **BSP** **/** **HAL** **packages** **unless** **given** **their** **own** **ATLAS** **slugs** — **separate** **concern** (`INFERRED`).  
- **Cygwin** **runtime** **as** **a** **full** **Windows** **POSIX** **layer** — **related** **but** **not** **this** **libc-only** **package** (`DOCUMENTED`).

## Versioning note

**Toolchain** **release** **bundles** **(GCC**/**newlib** **snapshots)** **drive** **visible** **changes** (`DOCUMENTED` **/** `OBSERVED`).
