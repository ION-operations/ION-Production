---
atlas_package: system
system_slug: argo-cd
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: B
---

# Architecture

- **Repo** **→** **Application** **spec** **→** **controller** **reconciliation** **→** **Kubernetes** **API** **per** **upstream** **component** **docs** (`DOCUMENTED`, `src-argo-cd-docs`).  
- **Contrasts** **with** **Flux’s** **split** **controllers** **and** **CRD** **shape** **while** **sharing** **GitOps** **goals** (`INFERRED` **comparative**).
