---
atlas_package: system
system_slug: fluxcd
schema_version: "1.0"
last_reviewed: "2026-04-11"
evidence_grade: B
---

# Architecture

- **Source** **→** **artifact** **(Kustomize** **/** **Helm)** **→** **reconcile** **→** **Kubernetes** **API** **apply** **loops** **per** **upstream** **component** **diagrams** (`DOCUMENTED`, `src-fluxcd-docs`).  
- **Contrasts** **with** **one-shot** **Helm** **CLI** **installs** **without** **continuous** **reconciliation** (`INFERRED` **comparative**).
