---
atlas_package: system
system_slug: kustomize
schema_version: "1.0"
last_reviewed: "2026-04-13"
evidence_grade: B
---

# Architecture

- **Base** **→** **overlay** **transforms** **→** **rendered** **Kubernetes** **YAML** **per** **upstream** **kustomize** **build** **model** (`DOCUMENTED`, `src-kustomize-docs`).  
- **Contrasts** **with** **Helm** **templating** **while** **often** **paired** **in** **pipelines** (`INFERRED` **comparative**).
