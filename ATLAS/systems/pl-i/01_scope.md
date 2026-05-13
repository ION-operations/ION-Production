---
atlas_package: system
system_slug: pl-i
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Historical origin** (NPL → MPPL → PL/I naming), IBM / SHARE committee context, **ANSI** standardization milestone (`DOCUMENTED` / `HISTORICAL`, `src-wiki-pl-i`, `src-ansi-pl-i-ref`).  
- **Language design themes:** block structure, rich types, I/O models, exception/interrupt handling, **orthogonality** as a stated design force (`DOCUMENTED`, `src-wiki-pl-i-goals`).  
- **Lineage:** languages influenced by / influencing PL/I (Fortran, COBOL, ALGOL, PL/M, Rexx, etc.) at **survey** depth (`DOCUMENTED`, `src-wiki-pl-i-influenced`).  
- **Relationship to Multics** documentation trail (`HISTORICAL`, `src-wiki-pl-i-multics`).

## Out of scope

- **Vendor-specific** optimizer behavior or z/OS product SKUs without a cited manual.  
- **Formal semantics** proof obligations (VDM / Vienna definition) beyond high-level pointer — **UNKNOWN** unless primary paper cited in ledger.

## Versioning note

**ANSI X3.53-1976** is a common **standard anchor**; later ISO/IEC revisions exist — pin exact standard ID for implementation claims (`DOCUMENTED` per standard catalog).
