---
atlas_package: system
system_slug: fluxcd
schema_version: "1.0"
last_reviewed: "2026-04-11"
evidence_grade: B
---

# Relation map (narrative)

- **`depends_on` `kubernetes`:** **controllers** **run** **on-cluster** (`DOCUMENTED`).  
- **`integrates_with` `helm`:** **HelmRepository**/**HelmRelease** **reconciliation** (`DOCUMENTED`).  
- **`integrates_with` `oci-image-spec` / `oci-distribution-spec`:** **image** **automation** **and** **registry** **traffic** (`INFERRED`).
