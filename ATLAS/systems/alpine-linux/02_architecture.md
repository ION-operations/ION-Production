---
atlas_package: system
system_slug: alpine-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Kernel** **packages** **+** **`musl`** **userland** **+** **`apk`** **managed** **trees** (`DOCUMENTED`).  
- **Init** **and** **service** **supervision** **via** **OpenRC** **by** **default** (`DOCUMENTED`).

## Delivery surfaces

- **Bare** **metal** **/** **VM** **installs**, **cloud** **images**, **and** **OCI** **base** **layers** (`DOCUMENTED` **/** `OBSERVED`).
