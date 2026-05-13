---
atlas_package: system
system_slug: oci-runtime-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `oci-image-spec`:** unpacked **rootfs** + generated **runtime** config align with image **config** (`DOCUMENTED`).  
- **`integrates_with` `linux-kernel`:** namespaces/cgroups/capabilities **back** the Linux profile (`DOCUMENTED`).  
- **`integrates_with` `runc`:** **reference implementation** (`DOCUMENTED`).  
- **`integrates_with` `crun`:** **alternative** **Linux** implementation (`DOCUMENTED`).  
- **`integrates_with` `docker` / `containerd` / `podman` / `cri-o` / `kubernetes`:** stacks **produce** and **execute** bundles (`DOCUMENTED`).
