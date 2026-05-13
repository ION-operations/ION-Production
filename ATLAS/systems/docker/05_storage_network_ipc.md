---
atlas_package: system
system_slug: docker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Storage, network, and IPC

- **Volumes and bind mounts** bridge host FS into containers (`DOCUMENTED`).  
- **Overlay-style image layers** as documented (`DOCUMENTED`).  
- **Networks:** published ports, DNS within user-defined networks (`DOCUMENTED`).  
- **IPC:** UNIX sockets to daemon API; container IPC modes (`DOCUMENTED`).
