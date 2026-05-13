---
atlas_package: system
system_slug: docker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Process, memory, and namespace model

- **Linux:** PID, mount, UTS, IPC, network, user namespaces + cgroups as used by Engine (`DOCUMENTED`, kernel + Docker docs).  
- **Windows containers:** different isolation technology — scope to documented Windows mode (`DOCUMENTED`).  
- **macOS Desktop:** Linux VM / virtualization layer hosts engine (`DOCUMENTED` product architecture summary).
