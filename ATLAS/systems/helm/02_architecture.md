---
atlas_package: system
system_slug: helm
schema_version: "1.0"
last_reviewed: "2026-04-10"
evidence_grade: B
---

# Architecture

- **Client** **→** **chart** **(tgz** **or** **OCI)** **→** **render** **→** **Kubernetes** **API** **apply** **path** **per** **upstream** **architecture** **docs** (`DOCUMENTED`, `src-helm-docs`).  
- **Contrasts** **with** **direct** **`kubectl`** **apply** **of** **static** **manifests** **without** **Helm** **release** **state** (`INFERRED` **comparative**).
