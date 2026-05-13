---
atlas_package: system
system_slug: docker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** primary Linux isolation substrate (`DOCUMENTED`).  
- **`integrates_with` `kubernetes`:** ecosystem and historical CRI-dockerd patterns (`DOCUMENTED`).  
- **`integrates_with` `containerd`:** Engine stack component (`DOCUMENTED`).  
- **`integrates_with` `systemd`:** common service packaging (`INFERRED`).  
- **`integrates_with` `aws-ecs`:** AWS ECS overview names Docker integration (`DOCUMENTED` via AWS ECS docs, cross-package).  
- **`integrates_with` `azure-container-apps`:** Azure Container Apps overview includes Docker Hub as an image source (`DOCUMENTED` via Microsoft Learn, cross-package).  
- **`integrates_with` `azure-aci`:** Azure Container Instances overview includes Docker Hub as an image source (`DOCUMENTED` via Microsoft Learn, cross-package).
