---
atlas_package: system
system_slug: linux-overlayfs
schema_version: "1.0"
last_reviewed: "2026-04-23"
evidence_grade: B
---

# Scope

## In scope

- **OverlayFS** **mount** **model** **(lower,** **upper,** **work,** **merged)** **and** **documented** **operational** **rules** (`DOCUMENTED`).  
- **Typical** **use** **in** **Linux** **container** **storage** **stacks** **as** **integration** **pattern** (`INFERRED`).  
- **Interaction** **with** **mount** **namespaces** **at** **survey** **level** (`INFERRED`).

## Out of scope

- **Vendor-specific** **graph** **driver** **internals** **beyond** **public** **kernel** **/** **runtime** **docs** **unless** **promoted** **as** **separate** **packages.**  
- **Non-Overlay** **union** **or** **snapshot** **filesystems** **—** **out** **unless** **scoped** **later**.

## Versioning note

**Feature** **flags** **and** **defaults** **evolve** **with** **kernel** **and** **distribution** **policy** (`OBSERVED`).
