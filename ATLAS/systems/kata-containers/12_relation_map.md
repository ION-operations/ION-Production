---
atlas_package: system
system_slug: kata-containers
schema_version: "1.0"
last_reviewed: "2026-04-07"
evidence_grade: B
---

# Relation map (narrative)

- **`implements` `oci-runtime-spec`:** **OCI** **bundle** **execution** **contract** (`DOCUMENTED`).  
- **`integrates_with` `kubernetes` + `containerd`:** **CRI** **/** **shim** **composition** (`DOCUMENTED`/`INFERRED`).  
- **`integrates_with` `qemu` + `linux-kvm`:** **Linux** **VM** **sandbox** **path** (`INFERRED`).  
- **`competes_with` `runc`:** **isolation** **mechanism** **substitution** (`INFERRED`).
