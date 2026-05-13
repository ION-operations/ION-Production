---
atlas_package: system
system_slug: kata-containers
schema_version: "1.0"
last_reviewed: "2026-04-07"
evidence_grade: B
---

# Scope

## In scope

- **OCI** **runtime** **integration,** **agent** **/** **shim** **components,** **and** **documented** **Kubernetes** **/** **CRI** **composition** (`DOCUMENTED`).  
- **QEMU/KVM** **usage** **patterns** **on** **Linux** **hosts** **at** **survey** **grain** (`INFERRED` **where** **marked**).

## Out of scope

- **Vendor** **Kubernetes** **distributions’** **private** **hardening** **unless** **sourced.**  
- **Guest** **kernel** **selection** **matrices** **per** **CPU** **vendor** **unless** **ledgered.**

## Versioning note

**Kata** **releases** **track** **QEMU,** **kernel,** **and** **OCI** **ecosystem** **changes** (`DOCUMENTED`).
