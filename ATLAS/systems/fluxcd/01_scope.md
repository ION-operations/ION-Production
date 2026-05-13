---
atlas_package: system
system_slug: fluxcd
schema_version: "1.0"
last_reviewed: "2026-04-11"
evidence_grade: B
---

# Scope

## In scope

- **Core** **controllers** **(source,** **kustomize,** **helm,** **notification,** **image-reflector/automation)** **and** **CRD** **surfaces** **per** **upstream** **docs** (`DOCUMENTED`).  
- **Git** **and** **OCI** **source** **reconciliation** **at** **survey** **grain** (`INFERRED` **where** **marked**).

## Out of scope

- **Hosted** **Flux** **SaaS** **pricing** **and** **SLAs.**  
- **Organization-wide** **policy** **without** **ledgered** **RBAC** **and** **repo** **layout.**

## Versioning note

**Flux** **v2** **release** **cadence** **and** **Kubernetes** **version** **support** **matrices** **are** **published** **upstream** (`DOCUMENTED`).
