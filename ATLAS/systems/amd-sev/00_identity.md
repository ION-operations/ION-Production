---
atlas_package: system
system_slug: amd-sev
schema_version: "1.0"
last_reviewed: "2026-04-07"
evidence_grade: B
---

# AMD Secure Encrypted Virtualization (SEV) — Identity

**Kind:** AMD memory encryption and guest isolation for virtual machines (SEV, SEV-ES, SEV-SNP per generation) (`DOCUMENTED` where AMD publishes PSP/SEV docs; claim granularity per CPU generation).

## Boundaries

- Not `intel-tdx` — different vendor ISA and firmware contract.
- Not `confidential-computing` alone — use both survey and vendor package for honest tiers.
