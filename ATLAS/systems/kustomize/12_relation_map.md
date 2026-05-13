---
atlas_package: system
system_slug: kustomize
schema_version: "1.0"
last_reviewed: "2026-04-13"
evidence_grade: B
---

# Relation map (narrative)

- **`depends_on` `kubernetes`:** **output** **is** **Kubernetes** **API** **YAML** (`DOCUMENTED`).  
- **`integrates_with` `helm`:** **post-render** **composition** (`DOCUMENTED`).  
- **`integrates_with` `fluxcd` + `argo-cd`:** **GitOps** **source** **types** (`DOCUMENTED`).
