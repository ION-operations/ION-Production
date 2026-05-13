---
atlas_package: system
system_slug: fortran
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Architecture (language)

## Execution model

**Procedures** and **modules** (modern); **COMMON** blocks (legacy) — evolution across standards (`DOCUMENTED`, `src-wiki-fortran`).

## Memory and arrays

**Column-major** array layout (culture for numerical linear algebra; **DOCUMENTED** in compiler docs). **Assumed-shape**, **allocatable**, **pointer** arrays — modern feature set (`DOCUMENTED`, `src-wiki-fortran`).

## Interoperability

**ISO_C_BINDING** — **C** interoperability module in modern Fortran (`DOCUMENTED`, `src-wiki-fortran`).

## Compilation model

Source → **compiler** → object code → **link** with runtime — same broad pattern as `systems/pl-i/` (`INFERRED` pipeline).
