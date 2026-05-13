---
atlas_package: system
system_slug: containerd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** execution substrate (`DOCUMENTED`).  
- **`integrates_with` `kubernetes`:** CRI (`DOCUMENTED`).  
- **`integrates_with` `docker`:** Engine delegation (`DOCUMENTED`).  
- **`integrates_with` `runc`:** typical low-level OCI runtime (`DOCUMENTED`).
