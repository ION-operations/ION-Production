---
atlas_package: system
system_slug: dwarf
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Standard** **sections** **(e.g.** **`.debug_*`**) **and** **conceptual** **DIE** **trees** (`DOCUMENTED`, `src-dwarfstd-home`).  
- **Versioning** **(DWARF** **3/4/5)** — **cite** **edition** **for** **exact** **layout** (`DOCUMENTED`).

## Out of scope

- **Proprietary** **debug** **formats** — **separate** **packages**.  
- **Runtime** **instrumentation** **(e.g.** **eBPF)** — **not** **DWARF** **proper** (`DOCUMENTED` boundary).

## Versioning note

**Consumers** **(debuggers)** **must** **match** **producer** **DWARF** **version** **features** (`DOCUMENTED` practice).
