---
atlas_package: system
system_slug: arm-cca
schema_version: "1.0"
last_reviewed: "2026-04-08"
evidence_grade: B
---

# ARM Confidential Compute Architecture (CCA) — Identity

**Kind:** ARM architecture security feature set for confidential computing (Realms, Realm Management Monitor) (`DOCUMENTED` at high level via Arm publications; microarch claims per CPU generation).

## Boundaries

- Not `intel-tdx` or `amd-sev` — different ISA and firmware trust model.
- Not `confidential-computing` alone — use survey plus this package for Arm-specific claims.
