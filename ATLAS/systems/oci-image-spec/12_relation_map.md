---
atlas_package: system
system_slug: oci-image-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `oci-distribution-spec`:** Registry HTTP APIs move manifests and layer blobs (`DOCUMENTED`).  
- **`integrates_with` `oci-runtime-spec`:** Unpacked images become **runtime bundles** (`DOCUMENTED`).  
- **`integrates_with` `docker`:** Engine builds and runs OCI-compatible images; spec is not Moby (`DOCUMENTED`).  
- **`integrates_with` `containerd` / `runc` / `crun` / `kubernetes`:** Typical pull → unpack → run path (`DOCUMENTED`).  
- **`competes_with` `systemd-portable`:** Overlapping “ship a runnable service tree” vs **portable OS-tree** bundles (`INFERRED`).
