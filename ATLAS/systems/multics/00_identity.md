---
atlas_package: system
system_slug: multics
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Multics — Identity

**Kind:** General-purpose, multi-user time-sharing OS research system (1960s–1980s).  
**Evidence boundary:** This package describes the **historical Multics design** from primary papers and contemporaneous technical books — not any modern reimplementation.

## Canonical definition

Multics was a joint MIT/GE/Bell Labs project delivering a secure, hierarchical time-sharing system with hardware-assisted protection, segmented virtual memory, and a unified information model influential on later OS research (`HISTORICAL`: `paper-corbato-1965-multics`, `paper-saltzer-1974-protection`, `paper-organick-1972-multics`).

## Boundaries

- **Not** a contemporary shipping product in this package’s scope.  
- **Not** equated with “Unix”; Unix was partly a reaction/simplification in a separate lineage (`HISTORICAL`, external Unix histories — add source when expanding).

## Why this system matters

- Established **protection as a first-class OS research problem** with concrete mechanisms (`HISTORICAL`, Saltzer et al.).  
- Explored **single-level store / unified memory–information** ideas that contrast with later “file descriptor + separate FS” designs (`HISTORICAL`).  
- Demonstrated **large-scale multi-user** engineering constraints that recur in cloud and enterprise systems (`HISTORICAL`).

## What this system teaches the atlas

- How to record **HISTORICAL** systems without retrofitting modern vocabulary as if contemporaneous.  
- How **lineage** differs from **fork** (Multics → research influence, not git ancestry to Linux).
