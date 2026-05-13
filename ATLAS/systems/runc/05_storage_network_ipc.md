---
atlas_package: system
system_slug: runc
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Storage, network, and IPC

- **Rootfs** provided by higher layer; runc mounts per `config.json` (`DOCUMENTED`).  
- **Network** namespaces created; interface setup often delegated to hooks/CNI (`DOCUMENTED` pattern).
