---
atlas_package: system
system_slug: helm
schema_version: "1.0"
last_reviewed: "2026-04-10"
evidence_grade: B
---

# Relation map (narrative)

- **`depends_on` `kubernetes`:** **chart** **targets** **the** **Kubernetes** **API** (`DOCUMENTED`).  
- **`integrates_with` `oci-distribution-spec`:** **OCI** **chart** **registry** **push/pull** (`DOCUMENTED`).  
- **`integrates_with` `oci-image-spec`:** **via** **workload** **image** **references** **in** **templates** (`INFERRED`).
