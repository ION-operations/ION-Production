---
atlas_package: system
system_slug: buildkit
schema_version: "1.0"
last_reviewed: "2026-04-09"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `oci-image-spec` + `oci-distribution-spec`:** **emits** **and** **pushes** **OCI** **artifacts** (`DOCUMENTED`).  
- **`integrates_with` `docker` + `containerd`:** **Engine** **and** **CRI-class** **storage** **integration** **paths** (`DOCUMENTED`).  
- **`integrates_with` `kubernetes`:** **in-cluster** **and** **CI** **pipelines** **adjacent** **to** **CRI** **pull** **paths** (`INFERRED`).
