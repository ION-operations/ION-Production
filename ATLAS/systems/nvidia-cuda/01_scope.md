---
atlas_package: system
system_slug: nvidia-cuda
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Toolkit** **components** **(compiler** **driver,** **libraries),** **runtime** **APIs** (`DOCUMENTED`, `src-cuda-docs`).  
- **OS** / **driver** **support** **matrices** (`DOCUMENTED`, `src-cuda-docs`).  

## Out of scope

- **Undocumented** **SASS** **encoding** — **§8** **gap** (`UNKNOWN` here).  
- **Cloud** **vendor** **managed** **GPU** **products** — **deployment** **layer** (`INFERRED`).

## Versioning note

**CUDA** **toolkit** **major** **versions** **change** **APIs** **and** **hardware** **support** — **pin** **release** (`DOCUMENTED`).
