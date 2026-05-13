---
atlas_package: system
system_slug: aws-ecs
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `docker`:** named third-party integration in AWS ECS overview (`DOCUMENTED`).  
- **`competes_with` `kubernetes` / `nomad`:** orchestrator substitution class (`INFERRED`).  
- **`competes_with` `aws-eks`:** AWS product-line pair (Kubernetes API vs ECS API) (`INFERRED`).  
- **`competes_with` `azure-container-apps`:** cross-vendor managed/serverless container platform class (`INFERRED`).  
- **`depends_on` `linux-kernel`:** typical Linux-backed capacity (`INFERRED`).
