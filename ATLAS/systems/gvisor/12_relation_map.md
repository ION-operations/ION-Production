---
atlas_package: system
system_slug: gvisor
schema_version: "1.0"
last_reviewed: "2026-04-08"
evidence_grade: B
---

# Relation map (narrative)

- **`implements` `oci-runtime-spec`:** **`runsc`** **bundle** **execution** (`DOCUMENTED`).  
- **`integrates_with` `kubernetes` + `containerd`:** **common** **deployment** **paths** (`DOCUMENTED`).  
- **`competes_with` `runc` + `kata-containers`:** **substitutable** **OCI** **runtimes** **with** **different** **isolation** **models** (`INFERRED`).
