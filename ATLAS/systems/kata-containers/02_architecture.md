---
atlas_package: system
system_slug: kata-containers
schema_version: "1.0"
last_reviewed: "2026-04-07"
evidence_grade: B
---

# Architecture

- **OCI** **bundle** **execution** **through** **a** **VM** **sandbox** **with** **supporting** **agents** **and** **shims** **as** **documented** **upstream** (`DOCUMENTED`, `src-kata-docs`).  
- **Contrasts** **with** **namespace-only** **low-level** **runtimes** **on** **Linux** **(see** **`runc`)** **at** **the** **isolation** **boundary** (`INFERRED` **comparative**).
