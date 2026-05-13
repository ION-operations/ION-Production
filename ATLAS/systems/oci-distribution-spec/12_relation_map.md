---
atlas_package: system
system_slug: oci-distribution-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `oci-image-spec`:** registries move **image** manifests and layer **blobs** defined by the image spec (`DOCUMENTED`).  
- **`integrates_with` `docker` / `containerd` / `podman` / `cri-o` / `kubernetes`:** clients and control planes **pull/push** via distribution-class APIs (`DOCUMENTED`).
