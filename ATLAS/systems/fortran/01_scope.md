---
atlas_package: system
system_slug: fortran
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Historical** lineage (1950s onward), **standard** milestones, **numeric** and **array** semantics at survey depth (`DOCUMENTED`, `src-wiki-fortran`).  
- **Co-array** / **parallel** features in modern standards — feature-level survey (`DOCUMENTED`, `src-wiki-fortran`).  
- **Relationship** to **C** and **PL/I** at lineage level (`DOCUMENTED`/`HISTORICAL`).

## Out of scope

- **Vendor** optimizer **vectorization** behavior without manual.  
- **GPU** Fortran (CUDA Fortran, OpenACC) — **PARTIAL** — add dedicated ledger rows when expanding.

## Versioning note

Pin **standard year** (e.g. Fortran 2018) for **standard-conforming** claims (`DOCUMENTED` per ISO edition).
