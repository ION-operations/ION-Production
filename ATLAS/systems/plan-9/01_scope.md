---
atlas_package: system
system_slug: plan-9
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Historical** Bell Labs context, release/licensing narrative at **survey** level (`DOCUMENTED`, `src-wiki-plan9-history`).  
- **Design themes:** 9P, **per-process namespace**, **union mounts**, **Fossil/Venti** (storage) as commonly summarized (`DOCUMENTED`, `src-wiki-plan9-components`).  
- **Userland** icons: **rio**, **acme**, **rc** shell — as named components in surveys (`DOCUMENTED`, `src-wiki-plan9`).  
- **Relationship to Unix** and to **Inferno** (`DOCUMENTED`, `src-wiki-inferno` cross-read).

## Out of scope

- **Live** cluster operations runbooks for a specific install — **UNKNOWN** without site docs.  
- **Performance** claims for 9P across WAN — **UNKNOWN** without benchmarks in ledger.

## Versioning note

Distributions and forks diverge — pin **distribution** when claiming behavior (`DOCUMENTED` per fork package).
