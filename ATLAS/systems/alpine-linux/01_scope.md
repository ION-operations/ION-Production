---
atlas_package: system
system_slug: alpine-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **Default** **userland** **choices** **documented** **by** **the** **Alpine** **project** — **`musl`**, **`apk`**, **OpenRC** **defaults** (`DOCUMENTED`, `src-alpine-about`).  
- **Relationship** **to** **common** **container** **and** **Kubernetes** **node** **patterns** **where** **Alpine** **bases** **appear** (`INFERRED` **/** **`DOCUMENTED`** **where** **cited**).

## Out of scope

- **`busybox`** **/** **`OpenRC`** **as** **standalone** **ATLAS** **packages** — **not** **seeded** (`INFERRED`).  
- **Every** **downstream** **vendor** **image** **that** **happens** **to** **use** **Alpine** — **track** **at** **image** **SBOM** **grain** (`INFERRED`).

## Versioning note

**Release** **branches** **and** **`apk`** **version** **pins** **define** **effective** **ABI** **and** **package** **sets** (`DOCUMENTED`).
